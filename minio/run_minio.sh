#!/bin/sh
export MINIO_VOLUMES_TMP_DIR=./minio_data/.minio.sys/tmp
./minio server ./minio_data/ --console-address :9001 
