# Resident Portal

## Docker run
Specify the server and secret

```sh
docker run -it --rm  -p 49190:49190/tcp -e SERVER=https://api-internal.v3box1.mosip.net -e RESIDENT_SECRET=<secret> --name resident mosipdev/resident_prototype_ui:develo
```

