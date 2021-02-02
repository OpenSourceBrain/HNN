
from neuromllite import Network, Cell, InputSource, Population, Synapse, RectangularRegion, RandomLayout
from neuromllite import Projection, RandomConnectivity, Input, Simulation
import sys

def generate(ref, np2=0, np5=0, nb2=0, nb5=0):
    ################################################################################
    ###   Build new network

    net = Network(id=ref)
    net.notes = 'Example: %s...'%ref

    net.seed = 7890
    net.temperature = 32

    net.parameters = { 'np2': np2,  'np5': np5,  'nb2': nb2,  'nb5': nb5, 'input_amp1':       0.3}

    l2p_cell = Cell(id='CELL_HH_reduced_L2Pyr', neuroml2_source_file='../CELL_HH_reduced_L2Pyr.cell.nml')
    net.cells.append(l2p_cell)


    '''input_source = InputSource(id='poissonFiringSyn', neuroml2_source_file='test_files/inputs.nml')
    net.input_sources.append(input_source)'''

    input_source1 = InputSource(id='i_clamp1',
                               pynn_input='DCSource',
                               parameters={'amplitude':'input_amp1', 'start':100, 'stop':300})

    net.input_sources.append(input_source1)
    '''
    input_source2 = InputSource(id='i_clamp2',
                               pynn_input='DCSource',
                               parameters={'amplitude':'input_amp2', 'start':500, 'stop':800})

    net.input_sources.append(input_source2)'''


    r1 = RectangularRegion(id='region1', x=0,y=0,z=0,width=1000,height=10,depth=1000)
    net.regions.append(r1)

    pop_l2p = Population(id='pop_l2p', size='np2', component=l2p_cell.id, properties={'color':'.7 0 0'},random_layout = RandomLayout(region=r1.id))

    net.populations.append(pop_l2p)

    '''
    net.synapses.append(Synapse(id='ampa', neuroml2_source_file='test_files/ampa.synapse.nml'))
    net.synapses.append(Synapse(id='gaba', neuroml2_source_file='test_files/gaba.synapse.nml'))


    net.projections.append(Projection(id='projEI',
                                      presynaptic=pE.id,
                                      postsynaptic=pRS.id,
                                      synapse='ampa',
                                      delay=2,
                                      weight=0.2,
                                      random_connectivity=RandomConnectivity(probability=.8))'''


    for pop_id in [pop_l2p.id]:
        net.inputs.append(Input(id='stim_%s'%pop_id,
                                input_source=input_source1.id,
                                population=pop_id,
                                percentage=100))

    print(net.to_json())
    new_file = net.to_json_file('%s.json'%net.id)


    ################################################################################
    ###   Build Simulation object & save as JSON

    sim = Simulation(id='Sim%s'%net.id,
                     network=new_file,
                     duration='1000',
                     seed='1111',
                     dt='0.025',
                     recordTraces={'all':'*:[0,1,2,3,4,5,6,7]'})

    sim.to_json_file()
    print(sim.to_json())

    return sim, net

################################################################################
###   Run in some simulators

from neuromllite.NetworkGenerator import check_to_generate_or_run
import sys


sim, net = generate('Pyr5s',np2=1)

check_to_generate_or_run(sys.argv, sim)
