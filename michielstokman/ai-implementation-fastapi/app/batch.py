import json
from pathlib import Path
from uuid import uuid4

from app.config import settings
from app.schemas import BatchRequest
from app.service import generate_content


async def run_batch(batch: BatchRequest) -> dict:
    results = []
    for item in batch.items:
        job_id = str(uuid4())[:12]
        try:
            generated = await generate_content(item)
            status = 'ready_for_review' if generated['moderation']['approved'] else 'blocked_by_moderation'
            results.append({'id': job_id, 'input': item.model_dump(), 'generated': generated, 'status': status})
        except Exception as exc:  # noqa: BLE001
            results.append({'id': job_id, 'input': item.model_dump(), 'status': 'failed', 'error': str(exc)})

    out_dir = Path(settings.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f'batch-{batch.month}-{uuid4().hex[:8]}.json'
    out_file.write_text(json.dumps({'batch': batch.model_dump(), 'results': results}, indent=2), encoding='utf-8')

    return {'output_file': str(out_file), 'results': results}
