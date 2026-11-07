const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const { test } = require("node:test");
const vm = require("node:vm");

const uid = "128492e27d6d44798f2ef9336fc1b2e7";
const since = "2026-11-06T00:00:00Z";
const key = "a".repeat(32);
const source = fs.readFileSync(path.join(__dirname, "inventario_work.js"), "utf8");

function file(n, project = true) {
    return {
        kind: "file", id: "item" + n, name: (project ? "CP12_CANDIDATO_P3_" + uid + "_" : "") + n + ".zip",
        library_file_id: "library" + n, file_id: "file" + n, size_bytes: 100 + n,
    };
}

async function run(pages) {
    const calls = [];
    const responses = [];
    let polled = false;
    const ok = (output = "") => ({ exit_code: 0, output });
    const tools = {
        async exec_command({ cmd }) {
            if (cmd.startsWith("'mktemp'")) return ok("../cp12-biblioteca.test\n");
            if (cmd.includes("'iniciar'")) return { session_id: 1, output: "" };
            if (cmd.includes("'esperar'")) {
                if (polled) return ok('{"exit_code":2}');
                polled = true;
                return ok(JSON.stringify({ key, request: { execution_uuid: uid, created_after: since } }));
            }
            if (cmd.startsWith("printf %s '")) {
                responses.push(JSON.parse(cmd.slice("printf %s '".length, cmd.indexOf("' | "))));
                return ok();
            }
            throw new Error("Comando inesperado");
        },
        async write_stdin() {
            return { exit_code: 2, output: "Bloqueo de prueba" };
        },
        async mcp__codex_apps__library_list(args) {
            calls.push(args);
            return { structuredContent: { surface: "library", warnings: [], ...pages[calls.length - 1] } };
        },
    };
    const execute = vm.runInNewContext(source, { tools });
    const result = await execute({ repositorio: "/proyecto", argumentos: ["retomar"], tamanoPagina: 2 });
    return { calls, responses, result };
}

test("consulta todas las páginas por cursor y entrega el inventario en una respuesta", async () => {
    const result = await run([
        { items: [file(1), file(2, false)], next_cursor: "cursor-opaco" },
        { items: [file(3)], next_cursor: null },
    ]);
    assert.equal(result.calls.length, 2);
    assert.equal(result.calls[0].filters.created_after, since);
    assert.equal(result.calls[1].cursor, "cursor-opaco");
    assert.deepEqual({ ...result.calls[1], cursor: undefined }, { ...result.calls[0], cursor: undefined });
    const { inventory } = result.responses[0];
    assert.equal(inventory.complete, true);
    assert.equal(inventory.items.length, 2);
    assert.equal(result.result.inventory_queries[0].pages, 2);
    assert.equal(result.result.exit_code, 2);
});

test("devuelve bloqueo si un cursor se repite", async () => {
    const result = await run([
        { items: [file(1)], next_cursor: "cursor" },
        { items: [file(2)], next_cursor: "cursor" },
    ]);
    assert.match(result.responses[0].error, /repetido/);
    assert.equal(result.responses[0].inventory, undefined);
});

test("una advertencia de página impide entregar un inventario parcial", async () => {
    const result = await run([
        { items: [file(1)], next_cursor: "cursor" },
        { items: [file(2)], warnings: ["incompleto"], next_cursor: null },
    ]);
    assert.match(result.responses[0].error, /página incompleta/);
    assert.equal(result.responses[0].inventory, undefined);
});
