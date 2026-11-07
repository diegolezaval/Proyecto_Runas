// Función para el runtime de herramientas de la sesión de ChatGPT Work.
(async function ejecutarCP12({ repositorio, argumentos, tamanoPagina = 200 }) {
    if (!Number.isInteger(tamanoPagina) || tamanoPagina < 1 || tamanoPagina > 200) {
        throw new Error("Tamaño de página de Biblioteca inválido");
    }
    const quote = (value) => "'" + value.replaceAll("'", "'\\''") + "'";
    const command = (cmd, yieldTime) => tools.exec_command({
        cmd,
        workdir: repositorio,
        max_output_tokens: 2000,
        yield_time_ms: yieldTime,
    });
    const shell = (parts) => parts.map(quote).join(" ");
    const poll = (session_id) => tools.write_stdin({ session_id, chars: "", yield_time_ms: 1000 });
    async function complete(cmd, yieldTime = 5000) {
        let result = await command(cmd, yieldTime);
        let output = result.output;
        while (result.session_id) {
            result = await poll(result.session_id);
            output += result.output;
        }
        return { ...result, output };
    }
    const script = "herramientas/inventario_cp12.py";
    const bootstrap = await complete(shell(["mktemp", "-d", "../cp12-biblioteca.XXXXXXXX"]));
    if (bootstrap.exit_code !== 0) throw new Error("No se pudo abrir el canal de Biblioteca");
    const channel = bootstrap.output.trim();

    async function collect({ execution_uuid, created_after }) {
        const start = new Date();
        const prefix = "CP12_CANDIDATO_P3_" + execution_uuid + "_";
        const args = {
            surface: "library",
            recursive: true,
            include_folders: false,
            limit: tamanoPagina,
            sort: "created_at",
            sort_order: "desc",
            filters: { created_after },
        };
        const cursors = new Set();
        const files = new Set();
        const items = [];
        let cursor;
        let pages = 0;
        do {
            if (pages >= 100) throw new Error("El listado superó el límite de páginas");
            let reply;
            try {
                reply = await tools.mcp__codex_apps__library_list(cursor ? { ...args, cursor } : args);
            } catch {
                throw new Error("La Biblioteca no respondió al listado");
            }
            if (reply.isError) throw new Error("La Biblioteca no confirmó el listado");
            const raw = reply.structuredContent ?? JSON.parse(
                reply.content.filter((part) => part.type === "text").map((part) => part.text).join("")
            );
            const page = raw.result ?? raw;
            if (page.surface !== "library" || !Array.isArray(page.items) ||
                    !Array.isArray(page.warnings) || page.warnings.length) {
                throw new Error("La Biblioteca devolvió una página incompleta");
            }
            pages += 1;
            for (const item of page.items) {
                if (item.kind !== "file") continue;
                if (typeof item.id !== "string" || files.has(item.id)) {
                    throw new Error("Identidad repetida o ausente al paginar la Biblioteca");
                }
                files.add(item.id);
                if (typeof item.name !== "string" || !item.name.startsWith(prefix)) continue;
                if (!item.library_file_id || !item.file_id || !Number.isSafeInteger(item.size_bytes) ||
                        item.size_bytes <= 0) {
                    throw new Error("Falta la identidad o el tamaño de un archivo CP12");
                }
                items.push({
                    id: item.id,
                    name: item.name,
                    library_file_id: item.library_file_id,
                    file_id: item.file_id,
                    size_bytes: item.size_bytes,
                });
            }
            cursor = page.next_cursor;
            if (cursor !== null && cursor !== undefined) {
                if (typeof cursor !== "string" || !cursor || cursors.has(cursor)) {
                    throw new Error("Cursor de Biblioteca inválido o repetido");
                }
                cursors.add(cursor);
            }
        } while (cursor);
        return {
            inventory: { captured_at: start.toISOString(), created_after, complete: true, items },
            receipt: { pages, files: files.size, cp12_files: items.length, seconds: (Date.now() - start) / 1000 },
        };
    }

    const began = Date.now();
    let process = await command(shell(["python3", script, "iniciar", channel, ...argumentos]), 1000);
    let output = process.output;
    let idle = 0;
    const queries = [];
    while (process.session_id) {
        const event = await complete(shell(["python3", script, "esperar", channel]), 14000);
        if (event.exit_code !== 0) throw new Error("El canal de Biblioteca dejó de responder");
        const next = JSON.parse(event.output);
        if (next.key) {
            idle = 0;
            let data;
            try {
                const result = await collect(next.request);
                queries.push(result.receipt);
                data = { key: next.key, inventory: result.inventory };
            } catch (error) {
                const reason = error instanceof Error ? error.message : "Consulta de Biblioteca incompleta";
                data = { key: next.key, error: reason.slice(0, 200) };
                queries.push({ error: data.error });
            }
            const response = await complete("printf %s " + quote(JSON.stringify(data)) + " | " +
                shell(["python3", script, "responder", channel]));
            if (response.exit_code !== 0) throw new Error("No se pudo entregar el inventario a reanudar_cp12.py");
        } else if (Number.isInteger(next.exit_code) || ++idle >= 3) {
            idle = 0;
            process = await poll(process.session_id);
            output += process.output;
        }
    }
    return { exit_code: process.exit_code, output, inventory_queries: queries, seconds: (Date.now() - began) / 1000 };
})
