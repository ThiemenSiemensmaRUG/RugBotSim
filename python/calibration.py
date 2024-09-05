
from webots_log_processor import WebotsProcessor
from utils import *


def compute_distance_directions(objects):
    pos_x = []
    pos_y = []

    for sim in objects:
        _,x,y,_ = sim.compute_distances_and_directions()
        pos_x.append(x)
        pos_y.append(y)

    x = create_one_array(pos_x)
    
    y = create_one_array(pos_y)

    plt.figure()
    plt.xlabel("X position [m]")
    plt.ylabel("Y position [m]")
    plt.hist2d(x,y,bins=np.linspace(-.2,.2,25))
    plt.colorbar()
    plt.clim(vmin =0,vmax = 40)
 


def compute_time_between_samples(objects):
    times = []
    for sim in objects:
        sim.data = sim.data[sim.data["robot_id"]!=2]
        times.append(np.array(sim.get_intersample_time()))
    times = create_one_array(times)
    plt.figure()
    plt.xlabel("Time [s]")
    plt.ylabel("Occurences")
    plt.hist(times, bins = np.linspace(1.4,7,20))


def get_ca_per_sample(objects):

    ca_per_sample = []
    for sim in objects:
        _,_,ca_per_sample_ = sim.get_state_times()
        ca_per_sample.append(create_one_array(ca_per_sample_))
    
    ca_per_samples = create_one_array(ca_per_sample) / 1000

    plt.figure()
    plt.ylim(0,4000)
    plt.hist(ca_per_samples,bins = np.linspace(-1,7,40))



def get_state_times(objects):
    ca_times = []
    sense_times = []
    for sim in objects:
        ca_time,sense_time,_= sim.get_state_times()
        ca_times.append(ca_time)
        sense_times.append(sense_time)
    
    ca_total = create_one_array(ca_times)
    sense_total = create_one_array(sense_times)

    plt.figure()
    plt.boxplot([ca_total,sense_total],labels=['CA','SENSE'])







calexp0 = WebotsProcessor("measurements/",'exp_cal_0.csv',1.55)
calexp1 = WebotsProcessor("measurements/",'exp_cal_1.csv',1.55)
calexp2 = WebotsProcessor("measurements/",'exp_cal_2.csv',1.55)

calsim0 = WebotsProcessor("/home/thiemenrug/Desktop/parallel_10/Instance_0/",'webots_log_0.txt',1.55)
calsim1 = WebotsProcessor("/home/thiemenrug/Desktop/parallel_10/Instance_1/",'webots_log_1.txt',1.55)
calsim2 = WebotsProcessor("/home/thiemenrug/Desktop/parallel_10/Instance_2/",'webots_log_2.txt',1.55)

sims = [calsim0,calsim1,calsim2]
exps = [calexp0,calexp1,calexp2]



get_ca_per_sample(sims)
get_ca_per_sample(exps)
plt.show()

# compute_time_between_samples(exps)
# compute_time_between_samples(sims)
# plt.show()
# compute_distance_directions(exps)
# compute_distance_directions(sims)


