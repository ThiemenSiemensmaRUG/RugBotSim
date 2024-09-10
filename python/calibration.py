
from webots_log_processor import WebotsProcessor
from utils import *
import pandas as pd
from scipy.stats import gamma,norm

# Generate a simple list of color names in Python

scolor = ["Blue", "Green", "Red", "Orange", "Gray", "White","Yellow", "Purple", "Black", "Cyan"]

def correlation(x,y,label):


    coer = np.corrcoef(x,y)[0,1]

    print(f"correlation for {label} = {round(coer*100,2)}%")


def plot_distance_direction(x_,label=None):
    _,x,y,_,dt = x_.compute_distances_and_directions()
    dt = dt.dropna()
    plt.figure()
    hist_dt,_,_,_ = plt.hist2d(dt['time'],dt['distance'],bins = (np.linspace(0,1200,25),np.linspace(0,.25,25)))

    plt.colorbar()
    plt.clim(vmin =0,vmax = 60)
    plt.xlabel("Time [s]")
    plt.ylabel("Distance [m]")
    plt.tight_layout()
    data = np.array(dt['distance'].dropna())
    data = data[data>0.07].copy()
    data = data[data<.7].copy()
   
    x_space = np.linspace(0.05,.3,25)
    shape, loc, scale = gamma.fit(data)
    shape = round(shape,5)
    loc = round(loc,5)
    scale = round(scale,5)
    pdf_fitted = gamma.pdf(x_space,shape,loc=loc,scale=scale)
    print("\n data distribution: ")
    print(f"shape: {shape}, loc: {loc}, scale: {scale}")
    plt.figure()
    hist_d,_,_ = plt.hist(data, bins=x_space, density=True, alpha=0.6)
    plt.xlabel("Distance [m]")
    plt.ylim([0,25])
    plt.plot(x_space, pdf_fitted, label=f'{label}: distance')
    plt.tight_layout()


    plt.figure()
    plt.xlabel("X position [m]")
    plt.ylabel("Y position [m]")
    hist_da,_,_,_ = plt.hist2d(x,y,bins=np.linspace(-.2,.2,40))
    plt.colorbar()
    plt.clim(vmin =0,vmax = 20)
    plt.tight_layout()
    return hist_dt,hist_d,hist_da


def plot_time_between_samples(x_):
    times = x_.get_intersample_time()
    times = times[times >3.15]
    plt.figure()
    plt.xlabel("Time [s]")
    plt.ylabel("Occurences")
    plt.hist(times, bins = np.linspace(1.4,7,100))

def get_ca_per_sample(x_,label):
    _,_,ca_per_sample_ = x_.get_state_times()
    samples = create_one_array(ca_per_sample_) / 1000
    samples = samples[samples > 0]
    
    bins = np.linspace(0,8000/1000,10*8)

    plt.figure()
    print(f"during {label}, {len(samples)} CA triggers")
    hist,_,_ = plt.hist(samples,alpha = .6,bins =bins,label = label,density=True)
    plt.xlabel("CA time per sample")
    plt.ylabel("Probability")
    plt.tight_layout()
    return hist

def plot_state_times(x_):
    ca_time,sense_time,_= x_.get_state_times()

    plt.figure()
    plt.ylim([0,400000])
    plt.boxplot([ca_time,sense_time],labels=['CA','SENSE'])

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
    plt.colorbar()
    plt.clim(vmin =0,vmax = 4)


def fit_distributions_measurements(x_,label = None,i=0):
    x_.add_labels()
    vib, nonvib = x_.get_samples()
   
    nonvib = nonvib[nonvib<3.2]
    vib = vib[vib<5.8]

    x_space = np.linspace(0,6,60)
    
    shape, loc, scale = gamma.fit(vib)
    shape = round(shape,5)
    loc = round(loc,5)
    scale = round(scale,5)
    print("\nVibration distribution: ")
    print(f"shape: {shape}, loc: {loc}, scale: {scale}")
    pdf_fitted = gamma.pdf(x_space, shape, loc=loc, scale=scale)
    plt.hist(vib, bins=x_space, density=True, alpha=0.6,color = scolor[0+i])
    plt.plot(x_space, pdf_fitted, label=f'{label}: Vibrating',color = scolor[0+i])

    print("cdf < $\\theta_c$: ",gamma.cdf(1.40,a=shape,scale = scale,loc = loc))
    shape, loc, scale = gamma.fit(nonvib)
    shape = round(shape,5)
    loc = round(loc,5)
    scale = round(scale,5)
    pdf_fitted = gamma.pdf(x_space,shape,loc=loc,scale=scale)
    print("\nNon Vibrating distribution: ")
    print(f"shape: {shape}, loc: {loc}, scale: {scale}")
    plt.xlabel("$O$")
    plt.ylabel("Probability")
    plt.hist(nonvib, bins=x_space, density=True, alpha=0.6,color = scolor[1+i])
    plt.plot(x_space, pdf_fitted, label=f'{label}: Non-vibrating',color = scolor[i+1])
    print("cdf > $\\theta_c$: ",1-gamma.cdf(1.40,a=shape,scale = scale,loc = loc))
    plt.axvline(1.4,color = 'black',linestyle = '--')
    plt.legend(loc = "upper right")
    plt.tight_layout()
    return shape,loc,scale

def sample_distribution(x_):
    plt.figure()
    hist,_,_,_ =plt.hist2d(x_.data['pos_x'],x_.data['pos_y'],bins = (5,5))
    plt.colorbar()
    plt.clim(vmin = 100,vmax =200)
    plt.xlabel("X position [m]")
    plt.ylabel("Y position [m]")
    plt.tight_layout()
    return hist

def concat_experiments(exps):

    for exp in exps[1:]:
    
        max_id = exps[0].data['robot_id'].max() +1
        exp.data['robot_id'] = exp.data['robot_id'] + max_id 
        exps[0].data = pd.concat([exps[0].data,exp.data])

    return exps[0]

def calibrate(x_):
    vibs = []
    errors_fn = []

    errors_fp = []
    for i in np.linspace(.5,4,200):
        x_.threshold = i
        x_.add_labels()
        fn_error = x_.fn_percentage / (x_.fn_percentage + x_.fp_percentage)
        fp_error = x_.fp_percentage / (x_.fn_percentage + x_.fp_percentage)
    
        errors_fn.append(fn_error)
        errors_fp.append(fp_error)
        vibs.append(i)
    plt.figure()
   
    
    plt.plot(vibs,errors_fn,label="FN")
    plt.plot(vibs,errors_fp,label = "FP")
    plt.axhline(0.48,label = "$0.48$",color = 'black',linestyle = '--')
    plt.axhline(0.52,label = "$0.52$",color = 'black',linestyle = '--')
    plt.axvline(1.4,label = "$\\theta_c = 1.4$",color = 'black',linestyle = '--')
    plt.xlabel("$\\theta_c$")
    plt.ylabel("1 / (FP+FN)")
    plt.legend(loc = 'upper right')
    plt.tight_layout()
    plt.show()


###main code for getting calibration values



vib_threshold = 1.40

calexp0 = WebotsProcessor("measurements/",'CAL_2.csv',vib_threshold)
calexp1 = WebotsProcessor("measurements/",'CAL_3.csv',vib_threshold)
calexp2 = WebotsProcessor("measurements/",'CAL_4.csv',vib_threshold)

vib_threshold = 1.40

calsim0 = WebotsProcessor("measurements/",'webots_log_0.txt',vib_threshold)
calsim1 = WebotsProcessor("measurements/",'webots_log_1.txt',vib_threshold)
calsim2 = WebotsProcessor("measurements/",'webots_log_2.txt',vib_threshold)

sims = [calsim0,calsim1,calsim2]
exps = [calexp0,calexp1,calexp2]

simulations = concat_experiments(sims)
experiments = concat_experiments(exps)

#calibrate(experiments)
print(experiments.fp_percentage)
print(experiments.fn_percentage)
print(experiments.tn_percentage)

print(simulations.fp_percentage)
print(simulations.fn_percentage)
print(simulations.tn_percentage)

# fit_distributions_measurements(experiments,"exp",0)
# fit_distributions_measurements(simulations,"sim",2)

# battery_sim, distance_sim, distance_angle_sim = plot_distance_direction(simulations)
# battery_exp, distance_exp, distance_angle_exp = plot_distance_direction(experiments)
# correlation(battery_exp,battery_sim,"Battery drainage")
# correlation(distance_exp,distance_sim,"Distance")
# correlation(distance_angle_exp,distance_angle_sim,"Distance & Bearing")

# amount_sim = sample_distribution(simulations)
# amount_exp = sample_distribution(experiments)

# correlation(amount_sim,amount_exp,"Distribution of samples")

ca_per_sample_sim = get_ca_per_sample(simulations,"sim")
ca_per_sample_exp = get_ca_per_sample(experiments,"exp")
correlation(ca_per_sample_exp,ca_per_sample_sim,"CA/Sample")

plt.show()


