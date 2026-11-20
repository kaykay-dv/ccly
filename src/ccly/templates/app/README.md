# __APP_NAME__

A Django app packaged for PyPI. Load it with ccly:

```bash
pip install -e .
ccly init __APP_NAME__
ccly migrate
ccly runserver
```

`GET /__APP_NAME__/health/` returns the JSON string `"OK"`.
