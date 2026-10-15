from pathlib import Path
import hashlib,json,zipfile

home=Path('mixed_transport_attempt')
out=Path('canonical_recovery_16');out.mkdir(exist_ok=False)
def sha(path):
 with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

results=[]
for label in ['TRANSPORTE_TAU_000016','NEGATIVO_TRANSPORTE_0008']:
 source=next((home/'capsules').glob('*'+label+'.zip'))
 destination=out/('CP12_MIXTO_CANONICO_'+label+'.zip')
 with zipfile.ZipFile(source) as original:
  manifest=json.loads(original.read('MANIFIESTO_NEGATIVO.json'))
  assert set(original.namelist())==set(manifest['files'])|{'MANIFIESTO_NEGATIVO.json'}
  excluded={n:v for n,v in manifest['files'].items() if any(p.startswith('.') for p in Path(n).parts)}
  selected={n:v for n,v in manifest['files'].items() if n not in excluded}
  for name,entry in manifest['files'].items():
   data=original.read(name);assert len(data)==entry['bytes'] and hashlib.sha256(data).hexdigest()==entry['sha256']
  note=dict(schema='CP12_CANONICAL_RECOVERY_AFTER_ADMINISTRATIVE_BACKUP_FAILURE',source_archive_sha256=sha(source),source_archive_bytes=source.stat().st_size,excluded_noncanonical_transfer_staging=excluded,scientific_state_receipt_and_sources_unchanged=True,M2_steps_executed=0,CP12_closed=False)
  note_bytes=(json.dumps(note,indent=2)+'\n').encode()
  manifest['files']={**selected,'preregistration/CANONICAL_RECOVERY.json':dict(bytes=len(note_bytes),sha256=hashlib.sha256(note_bytes).hexdigest())}
  manifest['canonical_selection_only']=True
  with zipfile.ZipFile(destination,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as zipped:
   for name in selected:zipped.writestr(name,original.read(name))
   zipped.writestr('preregistration/CANONICAL_RECOVERY.json',note_bytes)
   zipped.writestr('MANIFIESTO_NEGATIVO.json',json.dumps(manifest,indent=2)+'\n')
 with zipfile.ZipFile(destination) as zipped:
  check=json.loads(zipped.read('MANIFIESTO_NEGATIVO.json'))
  assert set(zipped.namelist())==set(check['files'])|{'MANIFIESTO_NEGATIVO.json'}
  for name,entry in check['files'].items():
   data=zipped.read(name);assert len(data)==entry['bytes'] and hashlib.sha256(data).hexdigest()==entry['sha256']
 results.append(dict(label=label,file=str(destination.resolve()),bytes=destination.stat().st_size,sha256=sha(destination),payload_files=len(manifest['files']),excluded_staging_files=len(excluded),scientific_bytes_unchanged=True))
(out/'PREPARACION_CANONICA.json').write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps(results))
