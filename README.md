This repository extends the NOPaxos repository: https://github.com/UWSysLab/NOPaxos  and Eduaterman repository: https://github.com/edauterman/NOPaxos by adding scripts to evaluate the performance of NOPaxos on a cloud platform. Specifically, it contains the benchmark script we used to recreate the Fig 3 and 5  from the NOPaxos paper on the gcloud platform.
Usage:
In order to perform the testing for experiment-3 using OpenStack, perform the following steps to setup the OpenStack Cloud:

	1. Install the openstack on gcloud instance (8vCPUs and 30GB RAM)
	The following is the link for the installation guide: https://docs.openstack.org/devstack/latest/
	We used a 1000 GB storage server for setup of the Gcloud instance.
	
	2. Configure the GUI on the Gcloud instance using the below instructional link: https://medium.com/google-cloud/graphical-user-interface-gui-for-google-compute-engine-instance-78fccda09e5c
	
	3. We used the below configurations for the OpenStack VM that hosts nodes including client, sequencer and replicas .Make sure IP forwarding is enabled and the machines are all in the same zone. Run the following commands on each machine:
	image: ubuntu16.6.4 qcow2
	instance flavor: m1.medium
	4GB RAM and 40GB disk
	
	4. Change the firewall settings to allow all SSH and TCP traffic
	
	5. Download the pem file
	
	6. ssh into the instance
	
	7. change the user permissions to get root access
	
	8. Download the code using  the following commands:
	sudo apt-get install git protobuf-compiler pkg-config libunwind-dev libssl-dev libprotobuf-dev libevent-dev make g++ lsof
	git clonehttps://github.com/Pooja8895/NoPaxos.git
	cd NOPaxos
	make PARANOID=0 
	
	9. Configure the DNS name and download auth file and source it : source alt_demo-openrc.sh
	Command to configure DNS : openstack subnet set --dns-nameserver 8.8.8.8 shared-subnet
	
	10. On each VM: Add the following line in /etc/resolv.conf file.
	nameserver 8.8.8.8 
	nameserver 8.8.4.4

	11. Install python3 on the VMs using the following commands:
	• sudo apt-get update
	• sudo apt-get -y upgrade
	• install python3 on the instance

	12. To recreate all figures, execute: bench/createFigures.sh. This will create 4 .png files: "Figure5-3.png", "Figure 5-5.png". Be advised that this script takes ~70 minutes to complete.
	
	13. To set up your own test environment1 client machine, 3/5/7 replica machines, and a sequencer, all fully configured. You will need to modify the configuration files (config-3, config-5, config-7, sequencer_config) to use the correct IP and MAC addresses and change bench/runBench.py to ssh into the correct machines.
	
	
