"""Inspect and acquire only the authorized official 14B checkpoint, without inference."""
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

os.environ['HF_HUB_DISABLE_PROGRESS_BARS'] = '1'
os.environ['HF_XET_CHUNK_CACHE_SIZE_BYTES'] = '0'
REPO = 'Qwen/Qwen2.5-14B-Instruct'
OUT = Path('artifacts/stage5/models/qwen14b')


def now():
    return datetime.now(timezone.utc).isoformat()


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(8 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def main():
    p = argparse.ArgumentParser()
    p.add_argument('phase', choices=['inspect', 'download'])
    p.add_argument('--model-path', required=True)
    args = p.parse_args()
    target = Path(args.model_path)
    from huggingface_hub import HfApi, hf_hub_download, snapshot_download
    if args.phase == 'inspect':
        if (OUT / 'inspection.json').exists():
            raise ValueError('Preserve prior inspection/revision resolution')
        started = time.monotonic()
        info = HfApi(token=False).model_info(REPO, files_metadata=True)
        names = {'LICENSE', 'README.md', 'config.json', 'generation_config.json',
                 'tokenizer.json', 'tokenizer_config.json', 'vocab.json', 'merges.txt',
                 'model.safetensors.index.json'}
        selected = [f for f in info.siblings if f.rfilename in names or f.rfilename.endswith('.safetensors')]
        files = {f.rfilename: {'size': f.size, 'git_blob_id': f.blob_id,
                               'lfs_sha256': f.lfs.sha256 if f.lfs else None} for f in selected}
        total = sum(f['size'] for f in files.values())
        free = shutil.disk_usage('/workspace').free
        if total > 40_000_000_000 or free < total + 2_000_000_000:
            raise RuntimeError('Authorized file-size or available-disk limit prevents download')
        cache_roots = [Path('/root/.cache/huggingface/hub'), Path('/workspace/models'),
                       Path('/workspace/apm-stage1/models'), target]
        cached_configs = sorted({str(f) for root in cache_roots if root.exists() for f in root.rglob('config.json')})
        inspection = {'repo_id': REPO, 'revision': info.sha, 'resolved_utc': now(),
                      'license': info.card_data.get('license'), 'source': 'Official Qwen organization on Hugging Face',
                      'source_url': f'https://huggingface.co/{REPO}/tree/{info.sha}',
                      'files': files, 'selected_file_bytes': total, 'disk_free_bytes_before': free,
                      'existing_cache_config_paths': cached_configs,
                      'gpu': subprocess.check_output(['nvidia-smi', '--query-gpu=name,memory.total,memory.used,driver_version', '--format=csv,noheader'], text=True).strip(),
                      'existing_gpu_processes': subprocess.check_output(['nvidia-smi', '--query-compute-apps=pid,process_name,used_memory', '--format=csv,noheader'], text=True).splitlines()}
        if inspection['license'] != 'apache-2.0':
            raise ValueError('Unexpected license; review before weights acquisition')
        # Small official metadata is inspected before acquiring checkpoint shards.
        for name in names:
            source = Path(hf_hub_download(REPO, name, revision=info.sha, local_dir=target, token=False))
            if name in {'LICENSE', 'README.md', 'config.json', 'generation_config.json', 'tokenizer_config.json', 'model.safetensors.index.json'}:
                dest = OUT / 'official' / name
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, dest)
        inspection['metadata_seconds'] = time.monotonic() - started
        save(OUT / 'inspection.json', inspection)
        print(json.dumps({k: inspection[k] for k in ['revision', 'license', 'selected_file_bytes', 'disk_free_bytes_before', 'gpu']}), flush=True)
        return
    inspection = json.loads((OUT / 'inspection.json').read_text())
    if (OUT / 'manifest.json').exists():
        raise ValueError('Checkpoint acquisition already completed; reuse it')
    log = OUT / 'acquisition.jsonl'
    started = time.monotonic()
    def event(value):
        with log.open('a') as f:
            f.write(json.dumps({'utc': now(), **value}) + '\n')
    event({'event': 'download_started', 'revision': inspection['revision'], 'authorized_file_bytes_limit': 40_000_000_000})
    try:
        snapshot_download(REPO, revision=inspection['revision'], local_dir=target,
                          allow_patterns=list(inspection['files']), token=False, max_workers=4)
        files = {}
        for name, expected in inspection['files'].items():
            path = target / name
            actual = sha(path)
            if path.stat().st_size != expected['size'] or (expected['lfs_sha256'] and actual != expected['lfs_sha256']):
                raise ValueError('Official checkpoint file mismatch: ' + name)
            if not expected['lfs_sha256']:
                blob = hashlib.sha1(b'blob ' + str(path.stat().st_size).encode() + b'\0' + path.read_bytes()).hexdigest()
                if blob != expected['git_blob_id']:
                    raise ValueError('Official metadata blob mismatch: ' + name)
            files[name] = {'bytes': path.stat().st_size, 'sha256': actual}
        save(OUT / 'manifest.json', {'model': REPO, 'revision': inspection['revision'], 'license': inspection['license'],
                                    'retrieved_utc': now(), 'files': files, 'total_file_bytes': sum(v['bytes'] for v in files.values()),
                                    'download_and_hash_seconds': time.monotonic() - started,
                                    'metadata_seconds': inspection['metadata_seconds'], 'new_model_files_limit': 40_000_000_000,
                                    'source_url': inspection['source_url'], 'existing_7b_weights_preserved': True})
        event({'event': 'download_finished', 'status': 'completed', 'elapsed_seconds': time.monotonic() - started})
        print('Official pinned 14B checkpoint acquired and all file hashes verified.', flush=True)
    except BaseException as exc:
        event({'event': 'download_finished', 'status': 'failed', 'elapsed_seconds': time.monotonic() - started,
               'error': f'{type(exc).__name__}: {exc}'})
        raise


if __name__ == '__main__':
    main()
