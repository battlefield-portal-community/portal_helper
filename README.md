# Portal Helper Bot
[![Amazon ECS](https://github.com/p0lygun/portal_helper/actions/workflows/aws.yml/badge.svg)](https://github.com/p0lygun/portal_helper/actions/workflows/aws.yml)  
  
A discord bot to display various things related to battlefield 2042's Portal Mode
Commands,  

- `/d` Show documenation of a block with its image
- `/tools` Shows Various Community made tools for Portal mode
- `experience info` Show Very helpful info about a experience made in Portal

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
