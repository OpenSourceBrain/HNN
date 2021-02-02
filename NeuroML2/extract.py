import neuroml
from pyneuroml import pynml

from pyneuroml.lems import generate_lems_file_for_neuroml

import neuroml.writers as writers

f= 'HNN.net.nml'
nml_doc = pynml.read_neuroml2_file(f)

print('Loaded information from: %s'%f)

net = nml_doc.networks[0]
net.id = '%s_inputs'%net.id
net_nml_doc = neuroml.NeuroMLDocument(id=net.id)

for ic in nml_doc.ion_channel_hhs:
    ic_nml_doc = neuroml.NeuroMLDocument(id=ic.id)
    ic_nml_doc.ion_channel_hhs.append(ic)
    nml_file = '%s.channel.nml'%ic.id
    writers.NeuroMLWriter.write(ic_nml_doc, nml_file)
    print('Saved ion channel to own file at %s'%nml_file)


for cell in nml_doc.cells:
    cell_nml_doc = neuroml.NeuroMLDocument(id=cell.id)
    cell_nml_doc.cells.append(cell)
    cd_added = []
    for cd in cell.biophysical_properties.membrane_properties.channel_densities:
        if not cd.ion_channel in cd_added:
            inc = neuroml.IncludeType('%s.channel.nml'%cd.ion_channel)
            cell_nml_doc.includes.append(inc)
            cd_added.append(cd.ion_channel)

    nml_file = '%s.cell.nml'%cell.id
    inc = neuroml.IncludeType(nml_file)
    net_nml_doc.includes.append(inc)
    writers.NeuroMLWriter.write(cell_nml_doc, nml_file)
    print('Saved cell to own file at %s'%nml_file)


syn_nml_doc = neuroml.NeuroMLDocument(id='HNN_Synapses')
for syn in nml_doc.exp_two_synapses:
    syn_nml_doc.exp_two_synapses.append(syn)
nml_file = '%s.nml'%syn_nml_doc.id
writers.NeuroMLWriter.write(syn_nml_doc, nml_file)
print('Saved synapses to own file at %s'%nml_file)
inc = neuroml.IncludeType(nml_file)
net_nml_doc.includes.append(inc)


net_nml_doc.networks.append(net)
nml_file = '%s.net.nml'%net.id
writers.NeuroMLWriter.write(net_nml_doc, nml_file)
print('Saved new network to own file at %s'%nml_file)



sim_id = 'Sim%s'%net.id
target = net.id
duration=1000
dt = 0.025
lems_file_name = 'LEMS_%s.xml'%sim_id
target_dir = "."

generate_lems_file_for_neuroml(sim_id,
                                   nml_file,
                                   target,
                                   duration,
                                   dt,
                                   lems_file_name,
                                   target_dir,
                                   include_extra_files = [],
                                   gen_plots_for_all_v = True,
                                   plot_all_segments = False,
                                   gen_plots_for_quantities = {},   #  Dict with displays vs lists of quantity paths
                                   gen_plots_for_only_populations = [],   #  List of populations, all pops if = []
                                   gen_saves_for_all_v = True,
                                   save_all_segments = False,
                                   gen_saves_for_only_populations = [],  #  List of populations, all pops if = []
                                   gen_saves_for_quantities = {},   #  Dict with file names vs lists of quantity paths
                                   gen_spike_saves_for_all_somas = True,
                                   report_file_name = 'report.%s.txt'%net.id,
                                   copy_neuroml = True,
                                   verbose=True)
