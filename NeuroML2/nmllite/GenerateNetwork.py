
from neuromllite import Network, Cell, InputSource, Population, Synapse, RectangularRegion, RandomLayout
from neuromllite import Projection, RandomConnectivity, Input, Simulation
import sys

def generate(ref, np2=0, np5=0, nb2=0, nb5=0, recordTraces='*'):
    ################################################################################
    ###   Build new network

    net = Network(id=ref)
    net.notes = 'Example: %s...'%ref

    net.seed = 7890
    net.temperature = 32

    net.parameters = { 'np2': np2,
                       'np5': np5,
                       'nb2': nb2,
                       'nb5': nb5,
                       'offset_curr_l2p': -0.05,
                       'weight_bkg_l2p': 0.01,
                       'weight_bkg_l5p': 0.01}

    l2p_cell = Cell(id='CELL_HH_reduced_L2Pyr', neuroml2_source_file='../CELL_HH_reduced_L2Pyr.cell.nml')
    net.cells.append(l2p_cell)
    l5p_cell = Cell(id='CELL_HH_reduced_L5Pyr', neuroml2_source_file='../CELL_HH_reduced_L5Pyr.cell.nml')
    net.cells.append(l5p_cell)
    l2b_cell = Cell(id='CELL_HH_simple_L2Basket', neuroml2_source_file='../CELL_HH_simple_L2Basket.cell.nml')
    net.cells.append(l2b_cell)
    l5b_cell = Cell(id='CELL_HH_simple_L5Basket', neuroml2_source_file='../CELL_HH_simple_L5Basket.cell.nml')
    net.cells.append(l5b_cell)


    input_source_poisson100 = InputSource(id='poissonFiringSyn100Hz', neuroml2_source_file='../inputs.nml')
    net.input_sources.append(input_source_poisson100)

    input_offset_curr_l2p = InputSource(id='input_offset_curr_l2p',
                               pynn_input='DCSource',
                               parameters={'amplitude':'offset_curr_l2p', 'start':0, 'stop':1e9})

    net.input_sources.append(input_offset_curr_l2p)



    l2 = RectangularRegion(id='L2', x=0,y=1000,z=0,width=1000,height=10,depth=1000)
    net.regions.append(l2)
    l5 = RectangularRegion(id='L5', x=0,y=0,z=0,width=1000,height=10,depth=1000)
    net.regions.append(l5)

    #https://github.com/OpenSourceBrain/OpenCortex
    import opencortex.utils.color as occ

    pop_l2p = Population(id='pop_l2p', size='np2', component=l2p_cell.id, properties={'color':occ.L23_PRINCIPAL_CELL},random_layout = RandomLayout(region=l2.id))
    net.populations.append(pop_l2p)
    pop_l5p = Population(id='pop_l5p', size='np5', component=l5p_cell.id, properties={'color':occ.L5_PRINCIPAL_CELL},random_layout = RandomLayout(region=l5.id))
    net.populations.append(pop_l5p)
    pop_l2b = Population(id='pop_l2b', size='nb2', component=l2b_cell.id, properties={'color':occ.L23_INTERNEURON},random_layout = RandomLayout(region=l2.id))
    net.populations.append(pop_l2b)
    pop_l5b = Population(id='pop_l5b', size='nb5', component=l5b_cell.id, properties={'color':occ.L5_INTERNEURON},random_layout = RandomLayout(region=l5.id))
    net.populations.append(pop_l5b)


    # L2 -> L2
    _add_projection(pop_l2p, pop_l2b, 'AMPA',        delay=0, weight=0.001, probability=0.8, net=net)
    _add_projection(pop_l2b, pop_l2p, 'L2Pyr_GABAA', delay=0, weight=0.001, probability=0.8, net=net)
    _add_projection(pop_l2b, pop_l2p, 'L2Pyr_GABAB', delay=0, weight=0.001, probability=0.8, net=net)

    # L2 -> L5
    _add_projection(pop_l2p, pop_l5p, 'L5Pyr_AMPA',  delay=0, weight=0.001, probability=0.8, net=net)
    _add_projection(pop_l2p, pop_l5b, 'AMPA',        delay=0, weight=0.001, probability=0.8, net=net)
    _add_projection(pop_l2b, pop_l5p, 'L5Pyr_GABAA', delay=0, weight=0.001, probability=0.8, net=net)

    # L5 -> L5
    _add_projection(pop_l5p, pop_l5b, 'AMPA',        delay=0, weight=0.001, probability=0.8, net=net)
    _add_projection(pop_l5b, pop_l5p, 'L5Pyr_GABAA', delay=0, weight=0.001, probability=0.8, net=net)
    _add_projection(pop_l5b, pop_l5p, 'L5Pyr_GABAB', delay=0, weight=0.001, probability=0.8, net=net)



    net.inputs.append(Input(id='stim_%s'%pop_l2p.id,
                            input_source=input_source_poisson100.id,
                            population=pop_l2p.id,
                            percentage=100,
                            weight='weight_bkg_l2p'))
    net.inputs.append(Input(id='stim_%s'%pop_l5p.id,
                            input_source=input_source_poisson100.id,
                            population=pop_l5p.id,
                            percentage=100,
                            weight='weight_bkg_l5p'))

    print(net.to_json())
    new_file = net.to_json_file('%s.json'%net.id)


    ################################################################################
    ###   Build Simulation object & save as JSON

    sim = Simulation(id='Sim%s'%net.id,
                     network=new_file,
                     duration='500',
                     seed='1111',
                     dt='0.025',
                     recordTraces={'all':recordTraces},
                     recordSpikes={'all':'*'})

    sim.to_json_file()
    print(sim.to_json())

    return sim, net

def _add_projection(pop_pre, pop_post, syn, delay, weight, probability, net):

    pre = pop_pre.id.split('_')[1]
    post = pop_post.id.split('_')[1]
    w = 'weight_%s_%s'%(pre,post)
    net.parameters[w]=weight

    syn_present = False

    for syn_nml in net.synapses:
        if syn_nml.id == syn:
            syn_present=True
    if not syn_present:
        net.synapses.append(Synapse(id=syn, neuroml2_source_file='../HNN_Synapses.nml'))

    net.projections.append(Projection(id='proj_%s_%s_%s'%(pre,post,syn),
                                      presynaptic=pop_pre.id,
                                      postsynaptic=pop_post.id,
                                      synapse=syn,
                                      delay=delay,
                                      weight=w,
                                      random_connectivity=RandomConnectivity(probability=probability)))

################################################################################
###   Run in some simulators

from neuromllite.NetworkGenerator import check_to_generate_or_run
import sys


if '-single' in sys.argv:
    sim, net = generate('Pyr5s',np5=1)
else:
    sim, net = generate('BiggerNet',np2=100,np5=100,nb2=35,nb5=35,recordTraces='[0,1,2]')

    sim, net = generate('BigNet',np2=5,np5=5,nb2=5,nb5=5,recordTraces='[0,1,2]')

check_to_generate_or_run(sys.argv, sim)
