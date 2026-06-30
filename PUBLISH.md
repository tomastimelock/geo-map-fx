# Publish geo-map-fx to PyPI

PyPI rate-limited during initial build session. Run this when the limit clears (usually 1h):

```bash
python -c "
from auth_api_key import get_key
import subprocess, sys
token = get_key('PYPI_TOKEN')
subprocess.run(
    [sys.executable, '-m', 'twine', 'upload', 'dist/*'],
    env={**__import__('os').environ, 'TWINE_USERNAME': '__token__', 'TWINE_PASSWORD': token},
    cwd=r'D:\PycharmProjects\trollfabriken-geo-map-fx-bootstrap\geo-map-fx'
)
"
```
