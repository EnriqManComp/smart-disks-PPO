# Smart Disks PPO
This project aims to find a potential solution to a search problem within a specified environment involving two players, utilizing Proximal Policy Optimization (PPO) as the AI algorithm.

## Problem Statement

The primary objective of this project is to implement an AI solution for the blue disk to search the vicinity of the red disk. It's worth noting that both disks can be considered as robots with the ability to move along the x and y axes.

<div align="center">
  <img src="https://raw.githubusercontent.com/EnriqManComp/smart-disks-PPO/master/result%20images/game%20environment.png" />
</div>

## States

The states represent distance measurements obtained from a laser in the x and y directions, as can be observed in the following figure

<div align="center">
  <img src="https://raw.githubusercontent.com/EnriqManComp/smart-disks-PPO/master/result%20images/laser.png" />
</div>

## Reward Model

The reward model is a combination of two reward functions. The first function provides the agent with a negative penalty if the disk enters the danger zone, where a collision could occur.

<div align="center">
  <img src="https://raw.githubusercontent.com/EnriqManComp/smart-disks-PPO/master/result%20images/fc_image.png" width="250px" height="250px" />
</div>

<br />
<div align="center">
  <img src="https://raw.githubusercontent.com/EnriqManComp/smart-disks-PPO/master/result%20images/fc_eq.png" width="400px" height="100px" />
</div>
<br />

The second function provides the agent with a positive reward proportional to the Euclidean distance between the two disks. Additionally, if the blue disk achieves its goal, it receives a higher reward.

<div align="center">
  <img src="https://raw.githubusercontent.com/EnriqManComp/smart-disks-PPO/master/result%20images/fp_image.png" width="250px" height="250px" />
</div>

<br />
<div align="center">
  <img src="https://raw.githubusercontent.com/EnriqManComp/smart-disks-PPO/master/result%20images/fp_eq.png" width="400px" height="100px" />
</div>
<br />

## Training results

<div align="center">
  <img src="https://raw.githubusercontent.com/EnriqManComp/smart-disks-PPO/master/result%20images/train_results.png" width="250px" height="250px" />
</div>

## Test results

<div align="center">
  <img src="https://raw.githubusercontent.com/EnriqManComp/smart-disks-PPO/master/result%20images/test%20results.png" width="250px" height="250px" />
</div>

## Video Demonstration

<div align="center">
  <img src="https://raw.githubusercontent.com/EnriqManComp/smart-disks-PPO/master/result%20images/smart-disk-PPO.gif" />
</div>

