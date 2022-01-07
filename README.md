# portal-docs-bot
[![Deploy to Amazon ECS ](https://github.com/p0lygun/portal_helper/actions/workflows/aws.yml/badge.svg) ](https://github.com/p0lygun/portal_helper/actions/workflows/aws.yml)  
This is a bot to display documentation of various blocks in Battlefield 2042's Portal logic builder,  use command `/d`

## How to run 

```
make a .env file with these vars
PD_LOG_LEVEL=10
PD_DISCORD_TOKEN=<your token>
PD_DEVELOPMENT=True
```

### Locally
```py
python -m bot
```

### production
```py
docker run -d --env-file .env ghcr.io/p0lygun/portal_helper:main
```
