# !/usr/bin/env sh

python -m torch.distributed.launch --nproc_per_node=2 ./tools/retrain.py \
            ./configs/fna_retinanet_fpn_retrain.py \
            --launcher pytorch \
            --seed 1 \
            --work_dir ./ \
            --data_path /mnt/mupengpeng_2021/dataset/coco/ \
