import pickle
import IPython
import argparse
import os

from utils import *


"""Parse input arguments."""
parser = argparse.ArgumentParser(description='SORT demo')
parser.add_argument('--display', dest='display', help='Display online tracker output (slow) [False]',
                    action='store_true')
parser.add_argument('--output_dir', default='/data/KITTI_object_tracking/spatio-temporal-map/raw_detection_map')

# parser.add_argument('--detection_data_pkl',
#                     default='/data/KITTI_object_tracking/results_PointRCNNTrackNet/detection_pkl/training_result.pkl')
parser.add_argument('--detection_data_pkl',
                    default='/data/KITTI_object_tracking/results_PointRCNNTrackNet/detection_pkl/training_result_RPN035_RCNN085.pkl')
parser.add_argument('--tracking_predict_pkl',
                    default='/data/KITTI_object_tracking/results_PointRCNNTrackNet/tracking_pkl/training_result.pkl')
parser.add_argument('--tracking_label_pkl',
                    default='/home/skwang/PYProject/draw_spatiol_temporal_map/pkl_data/training_label_result.pkl')
parser.add_argument('--pose_dir',
                    default='/data/KITTI_object_tracking/training/pose')
parser.add_argument('--velodyne_dir',
                    default='/data/KITTI_object_tracking/training/velodyne')

parser.add_argument('--data-dir', dest='data_dir', default='/data/KITTI_object_tracking/training')
parser.add_argument('--method', default='PointRCNN')

parser.add_argument('--frame', default='global', help="frame: -- global, -- inertial")

parser.add_argument('--map_duration_frame', default=10)

parser.add_argument('--is_test', default=False)
parser.add_argument('--seq_start', default= 20 )
parser.add_argument('--seq_end',   default= 20 )
args = parser.parse_args()

print("******************************************************")
print("*******************Detection Method*******************")
print("*********************", args.method, "**********************")
print("******************************************************\n")

type_whitelist = ('Car', 'Van')



dt_data = pickle.load(open(args.detection_data_pkl, 'rb'))
tracking_data = pickle.load(open(args.tracking_predict_pkl, 'rb'))
tracking_label_data = pickle.load(open(args.tracking_label_pkl, 'rb'))

for seq in range(args.seq_start, args.seq_end + 1):
    output_dir = os.path.join(args.output_dir, '%04d' % seq)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # get calib
    calib_path = os.path.join(args.data_dir, "calib", '%04d.txt' % seq)
    calib_seq = KittiCalib(calib_path).read_calib_file()
    T_cam_velo = calib_seq.Tr_cam_to_velo

    # get pose
    pose_seq = load_pose(args.velodyne_dir, args.pose_dir, seq)

    # map_num = math.ceil(len(det_seq) / args.map_duration_frame)
    MAX_ = 999999
    for i in range(MAX_):
        start_idx = int(args.map_duration_frame * i)
        end_idx = int(args.map_duration_frame * (i + 1))
        # get the detection result in this sequence
        det_seq = []
        for i in range(len(dt_data)):
            if dt_data[i]['metadata']['image_seq'] < seq:
                continue
            if dt_data[i]['metadata']['image_seq'] > seq:
                break
            if dt_data[i]['metadata']['image_idx'] < start_idx:
                continue
            if dt_data[i]['metadata']['image_idx'] >= end_idx:
                break
            det_seq.append(dt_data[i])

        if len(det_seq) == 0:
            break

        # get the predict tracking result in this sequence
        tracking_seq = []
        for i in range(len(tracking_data)):
            if tracking_data[i]['metadata']['image_seq'] < seq:
                continue
            if tracking_data[i]['metadata']['image_seq'] > seq:
                break
            if tracking_data[i]['metadata']['image_idx'] < start_idx:
                continue
            if tracking_data[i]['metadata']['image_idx'] >= end_idx:
                break
            tracking_seq.append(tracking_data[i])

        # get the label tracking result in this sequence
        tracking_label_seq = []
        for i in range(len(tracking_label_data)):
            if tracking_label_data[i]['metadata']['image_seq'] < seq:
                continue
            if tracking_label_data[i]['metadata']['image_seq'] > seq:
                break
            if tracking_label_data[i]['metadata']['image_idx'] < start_idx:
                continue
            if tracking_label_data[i]['metadata']['image_idx'] >= end_idx:
                break
            tracking_label_seq.append(tracking_label_data[i])


        # spatio_temporal_t_x_map_points = []
        # spatio_temporal_t_y_map_points = []
        spatio_temporal_t_x_y_map_points = []
        for j in range(len(det_seq)):
            centers = get_center_position_Lidar(det_seq[j], T_cam_velo)
            # ry_vecs = get_rotation_y_vec_Lidar(det_seq[j], T_cam_velo)
            for c in range(len(centers)):
                [x, y, z] = centers[c]
                t = det_seq[j]['metadata']['image_idx']

                if args.frame == 'global':
                    [x_global, y_global, z_global] = transform_points_from_inertial_to_global([x, y, z], pose_seq[t])
                    spatio_temporal_t_x_y_map_points.append([t, x_global, y_global])
                    # [ry_vec_x_global, ry_vec_y_global, ry_vec_z_global] = transform_rotation_y_from_inertial_to_global(
                    #     ry_vecs[c], pose_seq[t])
                    # print("in ", det_seq[j]['metadata'], ", ry_vec: ", [ry_vec_x_global, ry_vec_y_global, ry_vec_z_global])
                else:
                    # spatio_temporal_t_x_map_points.append([t, x])
                    # spatio_temporal_t_y_map_points.append([t, y])
                    spatio_temporal_t_x_y_map_points.append([t, x, y])
        # print("spatio_temporal_t_x_map_points: ", spatio_temporal_t_x_map_points)
        print("\nseq ", seq)
        print("frame from ", start_idx, " to ", end_idx)
        # print("visualize the t-x spatio-temporal map... time duration is ", args.map_duration_frame)
        # draw_points(spatio_temporal_t_x_map_points, vis=True)
        # print("visualize the t-y spatio-temporal map... time duration is ", args.map_duration_frame, "\n\n\n")
        # draw_points(spatio_temporal_t_y_map_points, vis=True)

        # print("visualize the t-x-y 3D spatio-temporal map... time duration is ", args.map_duration_frame, "\n\n\n")
        # draw_points(spatio_temporal_t_x_y_map_points, vis=True, v3d=True)

        pred_trajectories = get_trajectory(tracking_seq, T_cam_velo, pose_seq, type_whitelist, frame=args.frame)
        label_trajectories = get_trajectory(tracking_label_seq, T_cam_velo, pose_seq, type_whitelist, frame=args.frame)
        IPython.embed()
        draw_3d(spatio_temporal_t_x_y_map_points, pred_trajectories, label_trajectories, vis=True)
