# Arguments in order: #threads per machine, protocol, name of machine 1, name of machine 2, ...
import sys, string
import subprocess

def generateCmdStr(machine) : 
    return ("gcloud compute --project \"%s\" ssh --zone \"%s\" \"%s\" --command \"%s\"") % (project, zone, machine, remote_cmd)

# Parse args
if len(sys.argv) < 4:
    print("Required arguments: number of threads per machine, protocol, name of machine 1, name of machine 2, ...")
    exit
threads = string.atoi(sys.argv[1])
protocol = sys.argv[2]
machines = sys.argv[3:]

project = "nopaxos"
zone = "us-east1-b"
config = "config-3"
remote_cmd = ("cd ../anjalimishra/NOPaxos; rm output.txt; ./bench/client -t %d -c %s -n 1000 -m %s &> output.txt; python ./bench/combineThreadOutputs.py") % (threads, config, protocol)
tot_throughput = 0.0
tot_latency = 0.0

# Start all clients, non-blocking
processes = []
for machine in machines:
    process = subprocess.Popen(generateCmdStr(machine), shell=True, stdout=subprocess.PIPE)
    processes.append(process)

# Wait for output
for i, machine in enumerate(machines):
    output = processes[i].stdout.read() 
    outputLines = output.splitlines()
    elems = outputLines[0].split(":")
    tot_throughput += float(elems[1])
    elems = outputLines[1].split(":")
    tot_latency += float(elems[1])

# Collect output
#avg_throughput = tot_throughput / len(machines)
avg_latency = tot_latency / len(machines)

print((("Total throughput across %d machines each with %d threads running %s: %d") % (len(machines), threads, protocol, tot_throughput)))
print((("Average latency across %d machines each with %d threads running %s: %d") % (len(machines), threads, protocol, avg_latency)))
