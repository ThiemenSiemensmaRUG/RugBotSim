
from webots_log_processor import WebotsProcessor
from utils import *
import pandas as pd
from scipy.stats import gamma,norm

def plot_distance_direction(x_):
    _,x,y,_ = x_.compute_distances_and_directions()
    plt.figure()
    plt.xlabel("X position [m]")
    plt.ylabel("Y position [m]")
    plt.hist2d(x,y,bins=np.linspace(-.2,.2,25))
    plt.colorbar()
    plt.clim(vmin =0,vmax = 40)
 
def plot_time_between_samples(x_):
    times = x_.get_intersample_time()
    plt.figure()
    plt.xlabel("Time [s]")
    plt.ylabel("Occurences")
    plt.hist(times, bins = np.linspace(1.4,7,20))

def plot_ca_per_sample(x_):
    _,_,ca_per_sample_ = x_.get_state_times()
    plt.figure()
    plt.ylim(0,4000)
    plt.hist(ca_per_sample_,bins = np.linspace(-1,50,40))

def plot_state_times(x_):
    ca_time,sense_time,_= x_.get_state_times()
    ca_total = create_one_array(ca_time)
    sense_total = create_one_array(sense_time)
    plt.figure()
    plt.ylim([0,4000])
    plt.boxplot([ca_total,sense_total],labels=['CA','SENSE'])

def plot_vib_non_vib(x_):
    vib, nonvib = x_.get_samples()

    plt.figure()
    plt.hist(nonvib, bins = np.linspace(0,7,60), label = "$C=0$",alpha = .6)
    plt.hist(vib, bins = np.linspace(0,7,60), label = "$C=1$",alpha=.6)
    plt.axvline(x_.threshold,linestyle ='--',color = 'black')
    plt.legend()


def plot_measurements(x_):
    plt.figure()
    plt.scatter(x_.data["pos_x"], x_.data["pos_y"], s=5, c=x_.data['measurement'])


def fit_distributions_measurements(x_):
    x_.add_labels()
    vib, nonvib = x_.get_samples()
    vib = vib[vib>0]
    nonvib = nonvib[nonvib<3.9]

    x_space = np.linspace(0,6,60)
    
    shape, loc, scale = gamma.fit(vib)
    pdf_fitted = gamma.pdf(x_space, shape, loc=loc, scale=scale)
    plt.hist(vib, bins=x_space, density=True, alpha=0.6)
    plt.plot(x_space, pdf_fitted, 'r-', label='Vibrating')
    print(gamma.cdf(1.45,a=shape,scale = scale,loc = loc))



    shape, loc, scale = gamma.fit(nonvib)
    pdf_fitted = gamma.pdf(x_space,shape,loc=loc,scale=scale)


    plt.hist(nonvib, bins=x_space, density=True, alpha=0.6)
    plt.plot(x_space, pdf_fitted, 'r-', label='Non-vibrating')
    print(1-gamma.cdf(1.45,a=shape,scale = scale,loc = loc))
    plt.axvline(1.45,color = 'black',linestyle = '--')
    return shape,loc,scale




def concat_experiments(exps):

    for exp in exps[1:]:
    
        max_id = exps[0].data['robot_id'].max() +1
        exp.data['robot_id'] = exp.data['robot_id'] + max_id 
        exps[0].data = pd.concat([exps[0].data,exp.data])
    
    return exps[0]

def calibrate(x_):
    vibs = []
    errors = []
    for i in np.linspace(.5,4,200):
        x_.threshold = i
        x_.add_labels()
        f_error = x_.fn_percentage / (x_.fn_percentage + x_.fp_percentage)
        #print("Fault fill-ratio: ",round(f_error,3))
        errors.append(f_error)
        vibs.append(i)
    plt.figure()
    plt.plot(vibs,errors)
    plt.axhline(0.48,label = "$f=0.48$",color = 'black',linestyle = '--')
    plt.axvline(1.45,label = "$\\theta_c = 1.45$",color = 'black',linestyle = '--')
    plt.xlabel("$\\theta_c$")
    plt.ylabel("FN / (FP + FN)")
    plt.legend()
    plt.show()




vib_threshold = 1.45

calexp0 = WebotsProcessor("measurements/",'CAL_2.csv',vib_threshold)
calexp1 = WebotsProcessor("measurements/",'CAL_3.csv',vib_threshold)
calexp2 = WebotsProcessor("measurements/",'CAL_4.csv',vib_threshold)

calsim0 = WebotsProcessor("/home/thiemenrug/Desktop/parallel_10/Instance_0/",'webots_log_0.txt',vib_threshold)
calsim1 = WebotsProcessor("/home/thiemenrug/Desktop/parallel_10/Instance_1/",'webots_log_1.txt',vib_threshold)
calsim2 = WebotsProcessor("/home/thiemenrug/Desktop/parallel_10/Instance_2/",'webots_log_2.txt',vib_threshold)


sims = [calsim0,calsim1,calsim2]
exps = [calexp0,calexp1,calexp2]




experiments = concat_experiments(exps)
experiments.threshold = 1.45
experiments.add_labels()
print(experiments.tn_percentage)

fit_distributions_measurements(experiments)








plt.show()


