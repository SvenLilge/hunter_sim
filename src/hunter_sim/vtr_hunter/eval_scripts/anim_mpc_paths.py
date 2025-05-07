from argparse import ArgumentParser
from pathlib import Path

from matplotlib import pyplot as plt
import numpy as np
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
import matplotlib.animation as anim

from vtr_utils.bag_file_parsing import Rosbag2GraphFactory
from vtr_pose_graph.graph_iterators import PriviledgedIterator
import vtr_pose_graph.graph_utils as g_utils


import pandas as pd


def main(file_path, pose_graph_path):
    # Explicitly create a type store for legacy ROS2 bags without message definitions.
    typestore = get_typestore(Stores.ROS2_GALACTIC)

    leader_list = []
    follower_list = []

    # Create reader instance and open for reading.
    with AnyReader([Path(file_path)], default_typestore=typestore) as reader:
        connections = [x for x in reader.connections if 'mpc_prediction' in x.topic ]
        for connection, timestamp, rawdata in reader.messages(connections=connections):
            msg = reader.deserialize(rawdata, connection.msgtype)
            df_list = follower_list if "follower" in connection.topic else leader_list
            df_list.append({"t": msg.header.stamp.sec * 1e9 +  msg.header.stamp.nanosec, "x": [xi.pose.position.x for xi in msg.poses], "y":  [xi.pose.position.y for xi in msg.poses], "z":  [xi.pose.position.z for xi in msg.poses]})
    leader = pd.DataFrame(leader_list)
    follower = pd.DataFrame(follower_list)
    print(leader.shape)
    print(follower.shape)


    matched_follower = []
    for row_l in leader.itertuples(index=False):
        matched_follower.append(follower.loc[(follower['t']-row_l.t).abs().argsort()[0]].squeeze())
    matched_follower = pd.DataFrame(matched_follower)
    
    factory = Rosbag2GraphFactory(pose_graph_path)
    graph = factory.buildGraph()
    g_utils.set_world_frame(graph, graph.root)

    # print(f"Graph {graph} has {graph.number_of_vertices} vertices and {graph.number_of_edges} edges")
    x = []
    y = []
    t = []

    for v, e in PriviledgedIterator(graph.root):
        x.append(v.T_v_w.r_ba_ina()[0])
        y.append(v.T_v_w.r_ba_ina()[1])
        t.append(v.stamp)

    fig, ax = plt.subplots(figsize=(4.0, 3.6))
    teach_plot = ax.plot(x, y, label="Teach Path")[0]
    lead_plot = ax.plot(leader.iloc[0]['x'], leader.iloc[0]['y'], label="Leader")[0]
    follow_plot = ax.plot(matched_follower.iloc[0]['x'], matched_follower.iloc[0]['y'], label="Follower")[0]
    ax.legend()
    ax.set_xlabel("X (m)")
    ax.set_ylabel("Y (m)")
    ax.set_aspect('equal')

    def animate(i):
        lead_plot.set_xdata(leader.iloc[i]['x'])
        lead_plot.set_ydata(leader.iloc[i]['y'])
        follow_plot.set_xdata(matched_follower.iloc[i]['x'])
        follow_plot.set_ydata(matched_follower.iloc[i]['y'])
        x_min = min(min(matched_follower.iloc[i]['x']), min(leader.iloc[i]['x']))
        x_max = max(max(matched_follower.iloc[i]['x']), max(leader.iloc[i]['x']))
        x_av = (x_min + x_max) / 2
        y_min = min(min(matched_follower.iloc[i]['y']), min(leader.iloc[i]['y']))
        y_max = max(max(matched_follower.iloc[i]['y']), max(leader.iloc[i]['y']))
        y_av = (y_min + y_max) / 2
        ax.set_xlim([x_av - 5, x_av + 5])
        ax.set_ylim([y_av - 5, y_av + 5])
 
    #animate scatter plot
    ani = anim.FuncAnimation(fig, animate, 
                            frames = leader.shape[0], interval = 25, repeat = False)
    
    


    ani.save(filename=f"./test_sim.mp4", fps=30, dpi=300, writer="ffmpeg")


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("rosbag")
    parser.add_argument("pose_graph")
    args = parser.parse_args()
    main(args.rosbag, args.pose_graph)