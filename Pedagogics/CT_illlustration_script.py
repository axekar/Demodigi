import coin_tossing as ct                                               

p_vector = ct.np.linspace(0, 1, 100)                                    
posterior = ct.posterior(p_vector, 10, 5)                               
ct.plot_posterior(p_vector, posterior) 
