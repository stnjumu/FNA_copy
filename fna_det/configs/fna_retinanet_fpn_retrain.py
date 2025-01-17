# model settings
model = dict(
    type='RetinaNet',
    pretrained=dict(
        use_load=True,
        load_path='./seed_mbv2.pt',
        seed_num_layers=[1, 1, 2, 3, 4, 3, 3, 1, 1] # mbv2
        ),
    backbone=dict(
        type='FNA_Retinanet',
        net_config="""[[32, 16], ['k3_e1'], 1]|
[[16, 24], ['k7_e6', 'skip', 'k5_e3', 'k3_e3'], 2]|
[[24, 32], ['k7_e6', 'k5_e3', 'k5_e6', 'k7_e3'], 2]|
[[32, 64], ['k7_e6', 'k7_e3', 'k5_e6', 'k7_e3'], 2]|
[[64, 96], ['k5_e6', 'k5_e3', 'k5_e3', 'k7_e3'], 1]|
[[96, 160], ['k7_e6', 'k7_e3', 'k7_e3', 'k5_e3'], 2]|
[[160, 320], ['k7_e3'], 1]""",
        output_indices=[2, 3, 5, 7]
        ),
    neck=dict(
        type='FPN',
        in_channels=[24, 32, 96, 320],
        out_channels=256,
        start_level=1,
        add_extra_convs=True,
        num_outs=5),
    bbox_head=dict(
        type='RetinaHead',
        num_classes=81,
        in_channels=256,
        stacked_convs=4,
        feat_channels=256,
        octave_base_scale=4,
        scales_per_octave=3,
        anchor_ratios=[0.5, 1.0, 2.0],
        anchor_strides=[8, 16, 32, 64, 128],
        target_means=[.0, .0, .0, .0],
        target_stds=[1.0, 1.0, 1.0, 1.0]))
# training and testing settings
train_cfg = dict(
    assigner=dict(
        type='MaxIoUAssigner',
        pos_iou_thr=0.5,
        neg_iou_thr=0.4,
        min_pos_iou=0,
        ignore_iof_thr=-1),
    smoothl1_beta=0.11,
    gamma=2.0,
    alpha=0.25,
    allowed_border=-1,
    pos_weight=-1,
    debug=False)
test_cfg = dict(
    nms_pre=1000,
    min_bbox_size=0,
    score_thr=0.05,
    nms=dict(type='nms', iou_thr=0.5),
    max_per_img=100)
# dataset settings
dataset_type = 'CocoDataset'
img_norm_cfg = dict(
    mean=[123.675, 116.28, 103.53], std=[58.395, 57.12, 57.375], to_rgb=True)
data = dict(
    imgs_per_gpu=2,
    workers_per_gpu=2,
    train=dict(
        type=dataset_type,
        ann_file='annotations/instances_train2017.json',
        img_prefix='train2017/',
        img_scale=(1333, 800),
        img_norm_cfg=img_norm_cfg,
        size_divisor=32,
        flip_ratio=0.5,
        with_mask=False,
        with_crowd=False,
        with_label=True),
    val=dict(
        type=dataset_type,
        ann_file='annotations/instances_val2017.json',
        img_prefix='val2017/',
        img_scale=(1333, 800),
        img_norm_cfg=img_norm_cfg,
        size_divisor=32,
        flip_ratio=0,
        with_mask=False,
        with_crowd=False,
        with_label=True),
    test=dict(
        type=dataset_type,
        ann_file='annotations/instances_val2017.json',
        img_prefix='val2017/',
        img_scale=(1333, 800),
        img_norm_cfg=img_norm_cfg,
        size_divisor=32,
        flip_ratio=0,
        with_mask=False,
        with_crowd=False,
        with_label=False,
        test_mode=True))
# optimizer
optimizer = dict(type='SGD', lr=0.05, momentum=0.9, weight_decay=0.00005) # lr 0.05
optimizer_config = dict(grad_clip=dict(max_norm=35, norm_type=2))
# learning policy
lr_config = dict(
    policy='step',
    warmup='linear',
    warmup_iters=500,
    warmup_ratio=1.0 / 3,
    step=[8, 11])
checkpoint_config = dict(interval=1)
# yapf:disable
log_config = dict(
    interval=200,
    hooks=[
        dict(type='TextLoggerHook'),
        # dict(type='TensorboardLoggerHook')
    ])
# yapf:enable
# runtime settings
total_epochs = 12
use_syncbn = True
image_size_madds = (800, 1088)
device_ids = range(8)
dist_params = dict(backend='nccl')
log_level = 'INFO'
work_dir = './work_dirs/retinanet_FNA_fpn_1x'
load_from = None
resume_from = None
# workflow用于训练中是否验证，[('train', 1),('val', 1)]表示训练和验证交替进行
# 注意我观察本项目代码还没有实现验证相关代码
workflow = [('train', 1)] 
