import copy
_base_ = '../../base.py'
# Model settings
model = dict(
    type='BYOL',
    pretrained=None,
    base_momentum=0.996,
    backbone=dict(
        type='ResNet',
        depth=50,
        in_channels=3,
        out_indices=[4],  # 0: conv-1, x: stage-x
        norm_cfg=dict(type='BN')),
    neck=dict(
        type='NonLinearNeckV2',
        in_channels=2048,
        hid_channels=4096,
        out_channels=256,
        with_avg_pool=True),
    head=dict(type='LatentPredictHead',
              size_average=True,
              predictor=dict(type='NonLinearNeckV2',
                             in_channels=256, hid_channels=4096,
                             out_channels=256, with_avg_pool=False)))
# Dataset settings
data_source_cfg = dict(type='Cifar10', root='data')
# data_source_cfg = dict(
#     type='ImageNet',
#     memcached=True,
#     mclient_path='/mnt/lustre/share/memcached_client')
# data_train_list = 'data/imagenet/meta/train.txt'
# data_train_root = 'data/imagenet/train'
dataset_type = 'ClassificationDataset'
# dataset_type = 'BYOLDataset'
img_norm_cfg = dict(mean=[0.4914, 0.4822, 0.4465], std=[0.2023, 0.1994, 0.201])
# img_norm_cfg = dict(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
train_pipeline = [
    dict(type='RandomCrop', size=32, padding=4),
    dict(type='RandomHorizontalFlip'),
    dict(type='ToTensor'),
    dict(type='Normalize', **img_norm_cfg),
]
# train_pipeline = [
#     dict(type='RandomResizedCrop', size=224, interpolation=3), # bicubic
#     dict(type='RandomHorizontalFlip'),
#     dict(
#         type='RandomAppliedTrans',
#         transforms=[
#             dict(
#                 type='ColorJitter',
#                 brightness=0.4,
#                 contrast=0.4,
#                 saturation=0.2,
#                 hue=0.1)
#         ],
#         p=0.8),
#     dict(type='RandomGrayscale', p=0.2),
#     dict(
#         type='RandomAppliedTrans',
#         transforms=[
#             dict(
#                 type='GaussianBlur',
#                 sigma_min=0.1,
#                 sigma_max=2.0,
#                 kernel_size=23)
#         ],
#         p=1.),
#     dict(type='RandomAppliedTrans',
#          transforms=[dict(type='Solarization')], p=0.),
#     dict(type='ToTensor'),
#     dict(type='Normalize', **img_norm_cfg),
# ]
# train_pipeline1 = copy.deepcopy(train_pipeline)
# train_pipeline2 = copy.deepcopy(train_pipeline)
# train_pipeline2[4]['p'] = 0.1 # gaussian blur
# train_pipeline2[5]['p'] = 0.2 # solarization

test_pipeline = [
    dict(type='ToTensor'),
    dict(type='Normalize', **img_norm_cfg),
]

data = dict(
    imgs_per_gpu=128,
    workers_per_gpu=2,
    train=dict(
        type=dataset_type,
        data_source=dict(split='train', **data_source_cfg),
        pipeline=train_pipeline),
    val=dict(
        type=dataset_type,
        data_source=dict(split='test', **data_source_cfg),
        pipeline=test_pipeline),
    test=dict(
        type=dataset_type,
        data_source=dict(split='test', **data_source_cfg),
        pipeline=test_pipeline))
# data = dict(
#     imgs_per_gpu=32,  # total 32*8=256
#     workers_per_gpu=4,
#     train=dict(
#         type=dataset_type,
#         data_source=dict(
#             list_file=data_train_list, root=data_train_root,
#             **data_source_cfg),
#         pipeline1=train_pipeline1,
#         pipeline2=train_pipeline2))

# Additional hooks
custom_hooks = [
    dict(
        type='ValidateHook',
        dataset=data['val'],
        initial=True,
        interval=10,
        imgs_per_gpu=128,
        workers_per_gpu=8,
        eval_param=dict(topk=(1, 5)))
]
# custom_hooks = [
#     dict(type='BYOLHook', end_momentum=1.)
# ]
# Optimizer
optimizer = dict(type='SGD', lr=0.1, momentum=0.9, weight_decay=0.0005)
# optimizer = dict(type='LARS', lr=0.2, weight_decay=0.0000015, momentum=0.9,
#                  paramwise_options={
#                     '(bn|gn)(\d+)?.(weight|bias)': dict(weight_decay=0., lars_exclude=True),
#                     'bias': dict(weight_decay=0., lars_exclude=True)})
# Learning policy
lr_config = dict(policy='step', step=[150, 250])
# lr_config = dict(
#     policy='CosineAnnealing',
#     min_lr=0.,
#     warmup='linear',
#     warmup_iters=2,
#     warmup_ratio=0.0001, # cannot be 0
#     warmup_by_epoch=True)
checkpoint_config = dict(interval=50)
# checkpoint_config = dict(interval=10)
# Runtime settings
total_epochs = 350
# total_epochs = 200
