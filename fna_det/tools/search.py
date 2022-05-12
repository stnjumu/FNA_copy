from __future__ import division

import argparse
import numpy as np
import os
import os.path as osp
import sys
sys.path.append(osp.join(sys.path[0], '..'))
import time
import torch
#torch.backends.cudnn.enabled = False
import warnings
warnings.filterwarnings("ignore", category=UserWarning)

import models
from mmcv import Config
from mmdet import __version__
from mmdet.apis import init_dist, set_random_seed
from mmdet.datasets import get_dataset
from mmdet.models import build_detector
from tools import utils
from tools.apis.fna_search_apis import search_detector
from tools.divide_dataset import build_divide_dataset


def parse_args():
    parser = argparse.ArgumentParser(description='Train a detector')
    parser.add_argument('config', help='train config file path')
    parser.add_argument('--work_dir', type=str, help='the dir to save logs and models')
    parser.add_argument('--data_path', type=str, help='the data path')
    parser.add_argument('--job_name', type=str, default='', help='job name for output path')
    parser.add_argument(
        '--resume_from', help='the checkpoint file to resume from')
    parser.add_argument(
        '--validate',
        action='store_true',
        help='whether to evaluate the checkpoint during training')
    parser.add_argument(
        '--gpus',
        type=int,
        default=1,
        help='number of gpus to use '
        '(only applicable to non-distributed training)')
    parser.add_argument('--seed', type=int, default=None, help='random seed')
    parser.add_argument('--port', type=int, default=23333, help='random seed')
    parser.add_argument(
        '--launcher',
        choices=['none', 'pytorch', 'slurm', 'mpi'],
        default='none',
        help='job launcher')
    parser.add_argument('--local_rank', type=int, default=0)
    args = parser.parse_args()

    return args


def main():
    # 设置GPU, mu
    os.environ["CUDA_VISIBLE_DEVICES"]="3,4,5"

    args = parse_args()
    cfg = Config.fromfile(args.config) # 'mmcv.utils.config.ConfigDict'类型，是dict的子类；
    
    # set cudnn_benchmark
    if cfg.get('cudnn_benchmark', False):
        torch.backends.cudnn.benchmark = True
    # update configs according to CLI args
    # 输出文件夹
    if args.work_dir is not None:
        if args.job_name is '':                             # TODO: 命令行参数：现在是output，之后可改为其他名称;
            args.job_name = 'output'
        else:
            args.job_name = time.strftime("%Y%m%d-%H%M%S-") + args.job_name
        cfg.work_dir = osp.join(args.work_dir, args.job_name)
    
    # 继续训练，命令行参数和config都有，前者优先；
    if args.resume_from is not None:
        cfg.resume_from = args.resume_from
    cfg.gpus = args.gpus

    # init distributed env first, since logger depends on the dist info.
    if args.launcher == 'none':
        distributed = False
    else:
        distributed = True
        os.environ['MASTER_ADDR'] = 'localhost'
        os.environ['MASTER_PORT'] = '%d' % args.port
        init_dist(args.launcher, **cfg.dist_params)

    # init logger before other steps
    utils.create_work_dir(cfg.work_dir) # 这个函数在tools/utils.py, 依赖mmcv
    logger = utils.get_root_logger(cfg.work_dir, cfg.log_level)
    logger.info('Distributed training: {}'.format(distributed))
    logger.info('Search args: \n'+str(args))
    logger.info('Search configs: \n'+str(cfg))

    # ?? 这句什么用
    if cfg.checkpoint_config is not None:
        # save mmdet version in checkpoints as meta data
        cfg.checkpoint_config.meta = dict(
            mmdet_version=__version__, config=cfg.text)

    # set random seeds  
    if args.seed is not None:
        logger.info('Set random seed to {}'.format(args.seed))
        set_random_seed(args.seed)
    
    # 这句就是把cfg.data中数据集的相对路径前面加上args中的数据集路径，即绝对路径；
    utils.set_data_path(args.data_path, cfg.data)

    # 构建检测器
    model = build_detector(
        cfg.model, train_cfg=cfg.train_cfg, test_cfg=cfg.test_cfg)
    # models/fna_retinanet_detector.py BaseBackbone.get_sub_obj_list，可能与优化目标有关，可能是小trick
    model.backbone.get_sub_obj_list(cfg.sub_obj, (1, 3,)+cfg.image_size_madds)

    if cfg.use_syncbn: # FALSE
        model = utils.convert_sync_batchnorm(model)

    # train_data_ratio=0.5, 搜索和训练数据集不同；
    arch_dataset, train_dataset = build_divide_dataset(cfg.data, part_1_ratio=cfg.train_data_ratio)

    # TODO: 做到这了；
    search_detector(model, 
                    (arch_dataset, train_dataset),
                    cfg,
                    distributed=distributed,
                    validate=args.validate,
                    logger=logger)


if __name__ == '__main__':
    main()
