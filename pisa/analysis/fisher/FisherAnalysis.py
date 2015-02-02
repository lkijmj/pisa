#! /usr/bin/env python
#
# FisherAnalysis.py
#
# Runs the Fisher Analysis method
#
# author: Lukas Schulte - schulte@physik.uni-bonn.de
#         Sebastian Boeser - sboeser@uni-mainz.de
#

import numpy as np
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import tempfile

from pisa.utils.log import logging, profile, physics, set_verbosity
from pisa.utils.jsons import from_json,to_json
from pisa.analysis.TemplateMaker import TemplateMaker
from pisa.utils.params import select_hierarchy, get_free_params, get_values
from pisa.analysis.fisher.gradients import get_gradients


parser = ArgumentParser(description='''Runs a brute-force scan analysis varying a number of systematic parameters
defined in settings.json file and saves the likelihood values for all
combination of hierarchies.''',
                        formatter_class=ArgumentDefaultsHelpFormatter)
parser.add_argument('-t','--template_settings',type=str,
                    metavar='JSONFILE', required = True,
                    help='''Settings related to the template generation and systematics.''')
parser.add_argument('-g','--grid_settings',type=str,
                    metavar='JSONFILE', required = True,
                    help='''Settings for the grid on which the gradients are
                    calculated.''')
sselect = parser.add_mutually_exclusive_group(required=False)
sselect.add_argument('--save-templates',action='store_true',
                    default=True, dest='save_templates',
                    help="Save all the templates used to obtaine the gradients")
sselect.add_argument('--no-save-templates', action='store_false',
                    default=False, dest='save_templates',
                    help="Save just the fiducial templates")
parser.add_argument('-o','--outdir',type=str,default='fisher_data.json',metavar='DIR',
                    help="Output directory")
parser.add_argument('-v', '--verbose', action='count', default=None,
                    help='set verbosity level')
args = parser.parse_args()

set_verbosity(args.verbose)

#Read in the settings
template_settings = from_json(args.template_settings)
# this has only the number of test points in the parameter ranges and the chi2 criterion
grid_settings  = from_json(args.grid_settings)

#Here all the templates will be stored (temporarily):
template_directory = 

#Get the parameters
params = template_settings['params']
bins = template_settings['binning']

#Artifically add the hierarchy parameter to the list of parameters
#The method get_gradients below will know how to deal with it
params['hierarchy_nh'] = { "value": 0., "range": [0.,1.],
                           "fixed": False, "prior": None}
params['hierarchy_ih'] = { "value": 1., "range": [0.,1.],
                           "fixed": False, "prior": None}


#Get a template maker with the settings used to initialize
template_maker = TemplateMaker(get_values(params),**bins)

#Calculate both cases (NHM true and IMH true)
# TODO: This would run the analysis twice! do we need that?
for data_tag, data_normal in [('data_NMH',True),('data_IMH',False)]:

  #The fiducial params are selected from the hierachy case that does NOT match
  #the data, as we are varying from this model to find the 'best fit' 
  fiducial_params = select_hierarchy(params,not data_normal)

  #Get the free parameters (i.e. those for which the gradients should be calculated)
  free_params = select_hierarchy(get_free_params(params),not data_normal)

  gradient_maps = {}
  for param in free_params.keys():
    
    store_directory = args.outdir if args.save_templates else tempfile.gettempdir()
    
    gradient_maps[param] = get_gradients(param,
                                         template_maker,
                                         fiducial_params,
                                         grid_settings,
                                         store_directory)
    
  #fiducal_map = template_maker.get_template(get_values(fiducal_params))
  #fisher[data_tag] = build_fisher_matrix(gradient_maps,fiducial_map)

for channel in fisher[data_tag]:
    # add priors, labels, ...

for true_hierarchy in fisher:
    true_hierarchy[''] = true_hierarchy['cscd'] + true_hierarchy['trck']

#Outfile: fisher,
#         fiducial_templates (NH, IH),
#         templates?
#
#fisher = {'tracks' : type<FisherMatrix>,
#    'cascades': type<FisherMatrix>,
#    '': type<FisherMatrix>}
