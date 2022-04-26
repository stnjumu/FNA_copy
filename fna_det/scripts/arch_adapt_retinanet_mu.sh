# !/usr/bin/env sh

python -m torch.distributed.launch --nproc_per_node=4 ./tools/search.py \
            ./configs/fna_retinanet_fpn_search.py \
            --launcher pytorch \
            --seed 1 \
            --work_dir ./ \
            --data_path /mnt/mpp/dataset/coco/
