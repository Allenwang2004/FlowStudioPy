from flowstudio.tests.test_base import window
from flowstudio.flow_conf import *
from flowstudio.tests.common_functions import *
from flowstudio.nodes.SQRT_FP import FlowNodeSqrtFP
from flowstudio.nodes.ADDER_FP import FlowNodeAdderFP
from flowstudio.nodes.VISUALIZER import FLOW_Node_VISUALIZER
from flowstudio.nodes.DUMP import FLOW_Node_DUMP
from flowstudio.nodes.IN import FLOW_Node_IN
from flowstudio.nodes.OUT import FLOW_Node_OUT
from flowstudio.nodes.WAVPLAYER import FLOW_Node_WAVPLAYER
from flowstudio.nodes.TONEGEN import FLOW_Node_TONEGEN
from flowstudio.nodes.NOISEGEN import FLOW_Node_NOISEGEN
from flowstudio.nodes.CHIRP import FLOW_Node_CHIRP
from flowstudio.nodes.ADDER import FLOW_Node_ADDER
from flowstudio.nodes.NEGATOR import FLOW_Node_NEGATOR
from flowstudio.nodes.ABS import FLOW_Node_ABS
from flowstudio.nodes.SQRT import FLOW_Node_SQRT
from flowstudio.nodes.MULTIPLIER import FLOW_Node_MULTIPLIER
from flowstudio.nodes.SUBTRACTOR import FLOW_Node_SUBTRACTOR
from flowstudio.nodes.BIQUAD import FLOW_Node_BIQUAD
from flowstudio.nodes.PEQ import FLOW_Node_PEQ
from flowstudio.nodes.LPF import FLOW_Node_LPF
from flowstudio.nodes.HPF import FLOW_Node_HPF
from flowstudio.nodes.XOVER import FLOW_Node_XOVER
from flowstudio.nodes.IIRCOEF import FLOW_Node_IIRCOEF
from flowstudio.nodes.FIR import FLOW_Node_FIR
from flowstudio.nodes.GAIN import FLOW_Node_GAIN
from flowstudio.nodes.SMART_GAIN import FLOW_Node_SAMRT_GAIN
from flowstudio.nodes.ATTEN import FLOW_Node_ATTEN
from flowstudio.nodes.MUTE import FLOW_Node_MUTE
from flowstudio.nodes.LOUDNESS import FLOW_Node_LOUDNESS
from flowstudio.nodes.POLARITY import FLOW_Node_POLARITY
from flowstudio.nodes.LIMITER import FLOW_Node_LIMITER
from flowstudio.nodes.LIMITER_MB import FLOW_Node_LIMITER_MB
from flowstudio.nodes.COMP import FLOW_Node_COMP
from flowstudio.nodes.COMP_Combo import FLOW_Node_COMP_Combo
from flowstudio.nodes.CLIPPER import FLOW_Node_CLIPPER
from flowstudio.nodes.GATE import FLOW_Node_GATE
from flowstudio.nodes.SMART_GATE import FLOW_Node_SMART_GATE
from flowstudio.nodes.AUTO_COMP import FLOW_Node_AUTO_COMP
from flowstudio.nodes.MERGER import FLOW_Node_MERGER
from flowstudio.nodes.MUX import FLOW_Node_MUX
from flowstudio.nodes.DRYWET import FLOW_Node_DRYWET
from flowstudio.nodes.MIXER import FLOW_Node_MIXER
from flowstudio.nodes.DELAY import FLOW_Node_DELAY
from flowstudio.nodes.DELAY_Intp import FLOW_Node_DELAY_Intp
from flowstudio.nodes.MULTITAP import FLOW_Node_MULTITAP
from flowstudio.nodes.LONG_APF import FLOW_Node_LONG_APF
from flowstudio.nodes.LPF_COMB_FILTER import FLOW_Node_LPF_COMB_FILTER
# from flowstudio.nodes.REVERB import FLOW_Node_REVERB
from flowstudio.nodes.REVERB_V2 import FLOW_Node_REVERB_V2
from flowstudio.nodes.IR import FLOW_Node_IR
# from flowstudio.nodes.IR_ST import FLOW_Node_IR_ST
from flowstudio.nodes.CHORUS import FLOW_Node_CHORUS
from flowstudio.nodes.CROSSFEED import FLOW_Node_CROSSFEED
from flowstudio.nodes.VAD import FLOW_Node_VAD
from flowstudio.nodes.DBASS import FLOW_Node_DASS as FLOW_Node_DBASS
from flowstudio.nodes.DEESSER import FLOW_Node_DEESSER
from flowstudio.nodes.VBASS import FLOW_Node_VBASS
from flowstudio.nodes.AGC import FLOW_Node_AGC
from flowstudio.nodes.DLOUDNESS import FLOW_Node_DASS as FLOW_Node_DLOUDNESS
from flowstudio.nodes.BEAMFORMING import FLOW_Node_BEAMFORMING
from flowstudio.nodes.BEAMFORMING_2ch import FLOW_Node_BEAMFORMING_2ch
from flowstudio.nodes.BEAMFORMING_3ch import FLOW_Node_BEAMFORMING_3ch
from flowstudio.nodes.VAD_IABSE import FLOW_Node_VAD_IABSE
from flowstudio.nodes.AEC import FLOW_Node_ADDER as FLOW_Node_AEC
from flowstudio.nodes.AI_NR import FLOW_Node_AI_NR
from flowstudio.nodes.NOISEREDUCTION import FLOW_Node_NOISEREDCUTION
from flowstudio.nodes.SPATIALIZER import FLOW_Node_SPATIALIZER
from flowstudio.nodes.SUBPATCH import FLOW_Node_SUBPATCH
from flowstudio.nodes.METER import FLOW_Node_METER
from flowstudio.nodes.SPECTRUM import FLOW_Node_SPECTRUM
from flowstudio.nodes.RTA import FLOW_Node_RTA
from flowstudio.nodes.COMMENT import FLOW_Node_COMMENT
from flowstudio.nodes.IN_FP import FLOW_Node_IN_FP
from flowstudio.nodes.OUT_FP import FLOW_Node_OUT_FP
from flowstudio.nodes.HPF_FP import FLOW_Node_HPF_FP
from flowstudio.nodes.LPF_FP import FlowNodeLPFFP
from flowstudio.nodes.PEQ_FP import FLOW_Node_PEQ_FP
from flowstudio.nodes.ABS_FP import FLOW_Node_ABS_FP
from flowstudio.nodes.COMP_FP import FLOW_Node_COMP_FP
from flowstudio.nodes.LIMITER_FP import FLOW_Node_LIMITER_FP
from flowstudio.nodes.METER_FP import FLOW_Node_METER_FP
from flowstudio.nodes.MUX_FP import FLOW_Node_MUX_FP
from flowstudio.nodes.MUTE_FP import FLOW_Node_MUTE_FP
from flowstudio.nodes.GAIN_FP import FLOW_Node_GAIN_FP
from flowstudio.nodes.MUL_FP import FlowNodeMulFP
from flowstudio.nodes.LPF_FP import FlowNodeLPFFP
from flowstudio.nodes.XOVER_FP import FlowNodeXOverFP
from flowstudio.nodes.FIR_FP import FlowNodeFIRFP
from flowstudio.nodes.COMP_Combo_FP import FlowNodeCompComboFP
from flowstudio.nodes.CLIPPER_FP import FlowNodeClipperFP
from flowstudio.nodes.MIXER_FP import FlowNodeMixerFP
from flowstudio.nodes.DELAY_FP import FlowNodeDelayFP
from flowstudio.nodes.CINGO import FLOW_Node_CINGO
from flowstudio.nodes.UPHEAR_VQE import FLOW_Node_UPHEAR_VQE
from flowstudio.nodes.UPHEAR_VIRT import FLOW_Node_UPHEAR_VIRTUALIZER
from flowstudio.nodes.NTTS_IML import FLOW_Node_VCP
from flowstudio.nodes.NTTS_AGC import FlowNodeNTTSAGC
from flowstudio.nodes.DBASS_FP import FlowNodeDBassFP
from flowstudio.nodes.DYNAMIC_FILTER import FLOW_Node_DYNAMIC_FILTER
from flowstudio.nodes.AI_NR_48K import FlowNodeAINR48K
from flowstudio.nodes.AI_BF import FlowNodeAIBF
from flowstudio.nodes.VEP import FlowNodeVEP
from flowstudio.nodes.CLIPFIX import FLOW_Node_CLIPFIX
from flowstudio.nodes.SMART_EQ import FLOW_Node_SAMRT_EQ
from flowstudio.nodes.PEQ_V2 import FlowNodePEQADV
from flowstudio.nodes.DIRAC import FLOW_Node_DIRAC
from flowstudio.nodes.CINGO_SPK import FLOW_Node_CINGO_SPK
from flowstudio.nodes.FIR_LOAD import FLOW_Node_FIR_LOAD
from flowstudio.nodes.BIQUAD_LOAD import FLOW_Node_BIQUAD_LOAD
from flowstudio.nodes.CTC import FLOW_Node_CTC
from flowstudio.nodes.AI_NR_UC import FlowNodeAINRUC
from flowstudio.nodes.COHBF import FlowNodeCOHBF


# region COHBF
def test_add_coh_bf_ao_check_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()

    # Add the first node and verify the type
    main_sub_window.add_ao(OP_NODE_COHBF)
    make_all_sub_window_not_modified(window)
    node1 = main_sub_window.scene.nodes[0]
    assert isinstance(node1, FlowNodeCOHBF)

    # Add a second node and verify designer uniqueness
    main_sub_window.add_ao(OP_NODE_COHBF)
    make_all_sub_window_not_modified(window)
    node2 = main_sub_window.scene.nodes[1]
    assert node1.designator != node2.designator


# endregion

# region AI_NR_UC
def test_add_ai_nr_uc_ao_check_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()

    # Add the first node and verify the type
    main_sub_window.add_ao(OP_NODE_AI_NR_UC)
    make_all_sub_window_not_modified(window)
    node1 = main_sub_window.scene.nodes[0]
    assert isinstance(node1, FlowNodeAINRUC)


    # Add a second node and verify designer uniqueness
    main_sub_window.add_ao(OP_NODE_AI_NR_UC)
    make_all_sub_window_not_modified(window)
    node2 = main_sub_window.scene.nodes[1]
    assert node1.designator != node2.designator


# endregion

# region CTC
def test_add_ctc_ao_check_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()

    # Add the first node and verify the type
    main_sub_window.add_ao(OP_NODE_CTC)
    make_all_sub_window_not_modified(window)
    node1 = main_sub_window.scene.nodes[0]
    assert isinstance(node1, FLOW_Node_CTC)

    # Add a second node and verify designer uniqueness
    main_sub_window.add_ao(OP_NODE_CTC)
    make_all_sub_window_not_modified(window)
    node2 = main_sub_window.scene.nodes[1]
    assert node1.designator != node2.designator


# endregion

# region BIQUAD_LOAD
def test_add_biquad_load_ao_check_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()

    # Add the first node and verify the type
    main_sub_window.add_ao(OP_NODE_BIQUAD_LOAD, parameters={'num_bands': 1, 'num_channels': 1, 'control': False})
    make_all_sub_window_not_modified(window)
    node1 = main_sub_window.scene.nodes[0]
    assert isinstance(node1, FLOW_Node_BIQUAD_LOAD)

    # Add a second node and verify designer uniqueness
    main_sub_window.add_ao(OP_NODE_BIQUAD_LOAD, parameters={'num_bands': 1, 'num_channels': 1, 'control': False})
    make_all_sub_window_not_modified(window)
    node2 = main_sub_window.scene.nodes[1]
    assert node1.designator != node2.designator


# endregion

# region FIR_LOAD
def test_add_fir_load_ao_check_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()

    # Add the first node and verify the type
    main_sub_window.add_ao(OP_NODE_FIR_LOAD, parameters={'num_bands': 1, 'num_channels': 1, 'control': False})
    make_all_sub_window_not_modified(window)
    node1 = main_sub_window.scene.nodes[0]
    assert type(node1) == FLOW_Node_FIR_LOAD

    # Add a second node and verify designer uniqueness
    main_sub_window.add_ao(OP_NODE_FIR_LOAD, parameters={'num_bands': 1, 'num_channels': 1, 'control': False})
    make_all_sub_window_not_modified(window)
    node2 = main_sub_window.scene.nodes[1]
    assert node1.designator != node2.designator


# endregion

# region CINGO_SPK
def test_add_cingo_spk_ao_check_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()

    # Add the first node and verify the type
    main_sub_window.add_ao(OP_NODE_CINGO_SPK)
    make_all_sub_window_not_modified(window)
    node1 = main_sub_window.scene.nodes[0]
    assert type(node1) == FLOW_Node_CINGO_SPK

    # Add a second node and verify designer uniqueness
    main_sub_window.add_ao(OP_NODE_CINGO_SPK)
    make_all_sub_window_not_modified(window)
    node2 = main_sub_window.scene.nodes[1]
    assert node1.designator != node2.designator


# endregion

# region DIRAC
def test_add_dirac_ao_check_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()

    # Add the first node and verify the type
    main_sub_window.add_ao(OP_NODE_DIRAC, parameters={'configure': '2.0'})
    make_all_sub_window_not_modified(window)
    node1 = main_sub_window.scene.nodes[0]
    assert type(node1) == FLOW_Node_DIRAC

    # Add a second node and verify designer uniqueness
    main_sub_window.add_ao(OP_NODE_DIRAC, parameters={'configure': '5.1.2'})
    make_all_sub_window_not_modified(window)
    node2 = main_sub_window.scene.nodes[1]
    assert node1.designator != node2.designator


# endregion


# region PEQ_V2
def test_add_peq_v2_ao_check_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()

    # Add the first node and verify the type
    main_sub_window.add_ao(OP_NODE_PEQ_V2, parameters={'num_bands': 1, 'num_channels': 1, 'control': False})
    make_all_sub_window_not_modified(window)
    node1 = main_sub_window.scene.nodes[0]
    assert type(node1) == FlowNodePEQADV

    # Add a second node and verify designer uniqueness
    main_sub_window.add_ao(OP_NODE_PEQ_V2, parameters={'num_bands': 1, 'num_channels': 1, 'control': False})
    make_all_sub_window_not_modified(window)
    node2 = main_sub_window.scene.nodes[1]
    assert node1.designator != node2.designator


# endregion

# region SMART_EQ
def test_add_smart_eq_ao_check_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()

    # Add the first node and verify the type
    main_sub_window.add_ao(OP_NODE_SMART_EQ)
    make_all_sub_window_not_modified(window)
    node1 = main_sub_window.scene.nodes[0]
    assert type(node1) == FLOW_Node_SAMRT_EQ

    # Add a second node and verify designer uniqueness
    main_sub_window.add_ao(OP_NODE_SMART_EQ)
    make_all_sub_window_not_modified(window)
    node2 = main_sub_window.scene.nodes[1]
    assert node1.designator != node2.designator


# endregion

# region CLIPFIX
def test_add_clipfix_ao_check_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()

    # Add the first node and verify the type
    main_sub_window.add_ao(OP_NODE_CLIPFIX)
    make_all_sub_window_not_modified(window)
    node1 = main_sub_window.scene.nodes[0]
    assert type(node1) == FLOW_Node_CLIPFIX

    # Add a second node and verify designer uniqueness
    main_sub_window.add_ao(OP_NODE_CLIPFIX)
    make_all_sub_window_not_modified(window)
    node2 = main_sub_window.scene.nodes[1]
    assert node1.designator != node2.designator


# endregion

# region VEP
def test_add_vep_ao_check_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()

    # Add the first node and verify the type
    main_sub_window.add_ao(OP_NODE_VEP)
    make_all_sub_window_not_modified(window)
    node1 = main_sub_window.scene.nodes[0]
    assert type(node1) == FlowNodeVEP

    # Add a second node and verify designer uniqueness
    main_sub_window.add_ao(OP_NODE_VEP)
    make_all_sub_window_not_modified(window)
    node2 = main_sub_window.scene.nodes[1]
    assert node1.designator != node2.designator


# endregion

# region AI_BF
# def test_add_ai_bf_ao_check_ao_in_scene(window):
#     window.onFileNew()
#     main_sub_window = window.findMain().widget()
#     main_sub_window.add_ao(OP_NODE_AI_BF)
#     make_all_sub_window_not_modified(window)
#     assert type(main_sub_window.scene.nodes[0]) == FlowNodeAIBF


# def test_add_two_ai_bf_ao_check_designator_different(window):
#     window.onFileNew()
#     main_sub_window = window.findMain().widget()
#     main_sub_window.add_ao(OP_NODE_AI_BF)
#     main_sub_window.add_ao(OP_NODE_AI_BF)
#     make_all_sub_window_not_modified(window)
#     assert main_sub_window.scene.nodes[0].designator != main_sub_window.scene.nodes[1].designator


# endregion

# region AI_NR_48K
def test_add_ai_nr_48k_ao_check_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()

    # Add the first node and verify the type
    main_sub_window.add_ao(OP_NODE_AI_NR_48K)
    make_all_sub_window_not_modified(window)
    node1 = main_sub_window.scene.nodes[0]
    assert type(node1) == FlowNodeAINR48K

    # Add a second node and verify designer uniqueness
    main_sub_window.add_ao(OP_NODE_AI_NR_48K)
    make_all_sub_window_not_modified(window)
    node2 = main_sub_window.scene.nodes[1]
    assert node1.designator != node2.designator


# endregion

# region DYNAMIC_FILTER
def test_add_dynamic_filter_ao_check_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()

    # Add the first node and verify the type
    main_sub_window.add_ao(OP_NODE_DYNAMIC_FILTER)
    make_all_sub_window_not_modified(window)
    node1 = main_sub_window.scene.nodes[0]
    assert type(node1) == FLOW_Node_DYNAMIC_FILTER

    # Add a second node and verify designer uniqueness
    main_sub_window.add_ao(OP_NODE_DYNAMIC_FILTER)
    make_all_sub_window_not_modified(window)
    node2 = main_sub_window.scene.nodes[1]
    assert node1.designator != node2.designator


# endregion

# region DBASS_FP AO
def test_add_dbass_fp_ao_check_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()

    # Add the first node and verify the type
    main_sub_window.add_ao(OP_NODE_DBASS_FP, parameters={'num_channels': 1})
    make_all_sub_window_not_modified(window)
    node1 = main_sub_window.scene.nodes[0]
    assert type(node1) == FlowNodeDBassFP

    # Add a second node and verify designer uniqueness
    main_sub_window.add_ao(OP_NODE_DBASS_FP, parameters={'num_channels': 1})
    make_all_sub_window_not_modified(window)
    node2 = main_sub_window.scene.nodes[1]
    assert node1.designator != node2.designator


# endregion

# region NTTS_AGC AO
def test_add_ntts_agc_ao_check_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()

    # Add the first node and verify the type
    main_sub_window.add_ao(OP_NODE_NTTS_AGC, parameters={'num_channels': 1})
    make_all_sub_window_not_modified(window)
    node1 = main_sub_window.scene.nodes[0]
    assert type(node1) == FlowNodeNTTSAGC

    # Add a second node and verify designer uniqueness
    main_sub_window.add_ao(OP_NODE_NTTS_AGC, parameters={'num_channels': 1})
    make_all_sub_window_not_modified(window)
    node2 = main_sub_window.scene.nodes[1]
    assert node1.designator != node2.designator


# endregion

# region NTTS_IML AO
def test_add_ntts_iml_ao_check_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()

    # Add the first node and verify the type
    main_sub_window.add_ao(OP_NODE_NTTS_IML)
    make_all_sub_window_not_modified(window)
    node1 = main_sub_window.scene.nodes[0]
    assert type(node1) == FLOW_Node_VCP

    # Add a second node and verify designer uniqueness
    main_sub_window.add_ao(OP_NODE_NTTS_IML)
    make_all_sub_window_not_modified(window)
    node2 = main_sub_window.scene.nodes[1]
    assert node1.designator != node2.designator


# endregion

# region UPHEAR_VIRT AO
def test_add_uphear_virt_ao_check_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()

    # Add the first node and verify the type
    main_sub_window.add_ao(OP_NODE_UPHEAR_VIRT)
    make_all_sub_window_not_modified(window)
    node1 = main_sub_window.scene.nodes[0]
    assert type(node1) == FLOW_Node_UPHEAR_VIRTUALIZER

    # Add a second node and verify designer uniqueness
    main_sub_window.add_ao(OP_NODE_UPHEAR_VIRT)
    make_all_sub_window_not_modified(window)
    node2 = main_sub_window.scene.nodes[1]
    assert node1.designator != node2.designator


# endregion


# region UPHEAR_VQE AO
def test_add_uphear_vqe_ao_check_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()

    # Add the first node and verify the type
    main_sub_window.add_ao(OP_NODE_UPHEAR_VQE, parameters={'num_in_channels': 1, 'num_out_channels': 1})
    make_all_sub_window_not_modified(window)
    node1 = main_sub_window.scene.nodes[0]
    assert type(node1) == FLOW_Node_UPHEAR_VQE

    # Add a second node and verify designer uniqueness
    main_sub_window.add_ao(OP_NODE_UPHEAR_VQE, parameters={'num_in_channels': 1, 'num_out_channels': 1})
    make_all_sub_window_not_modified(window)
    node2 = main_sub_window.scene.nodes[1]
    assert node1.designator != node2.designator


# endregion

# region CINGO AO
def test_add_cingo_ao_check_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()

    # Add the first node and verify the type
    main_sub_window.add_ao(OP_NODE_CINGO, parameters={'configure': '2.0'})
    make_all_sub_window_not_modified(window)
    node1 = main_sub_window.scene.nodes[0]
    assert type(node1) == FLOW_Node_CINGO

    # Add a second node and verify designer uniqueness
    main_sub_window.add_ao(OP_NODE_CINGO, parameters={'configure': '7.1'})
    make_all_sub_window_not_modified(window)
    node2 = main_sub_window.scene.nodes[1]
    assert node1.designator != node2.designator


# endregion


# region DELAY_FP AO
def test_add_delay_fp_ao_check_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()

    # Add the first node and verify the type
    main_sub_window.add_ao(OP_NODE_DELAY_FP, parameters={'num_channels': 1})
    make_all_sub_window_not_modified(window)
    node1 = main_sub_window.scene.nodes[0]
    assert type(node1) == FlowNodeDelayFP

    # Add a second node and verify designer uniqueness
    main_sub_window.add_ao(OP_NODE_DELAY_FP, parameters={'num_channels': 1})
    make_all_sub_window_not_modified(window)
    node2 = main_sub_window.scene.nodes[1]
    assert node1.designator != node2.designator


# endregion

# region MIXER_FP AO
def test_add_mixer_fp_ao_check_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()

    # Add the first node and verify the type
    main_sub_window.add_ao(OP_NODE_MIXER_FP, parameters={'num_in_channels': 1, 'num_out_channels': 1})
    make_all_sub_window_not_modified(window)
    node1 = main_sub_window.scene.nodes[0]
    assert type(node1) == FlowNodeMixerFP

    # Add a second node and verify designer uniqueness
    main_sub_window.add_ao(OP_NODE_MIXER_FP, parameters={'num_in_channels': 1, 'num_out_channels': 1})
    make_all_sub_window_not_modified(window)
    node2 = main_sub_window.scene.nodes[1]
    assert node1.designator != node2.designator


# endregion

# region CLIPPER_FP AO
def test_add_clipper_fp_ao_check_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()

    # Add the first node and verify the type
    main_sub_window.add_ao(OP_NODE_CLIPPER_FP, parameters={'num_channels': 1})
    make_all_sub_window_not_modified(window)
    node1 = main_sub_window.scene.nodes[0]
    assert type(node1) == FlowNodeClipperFP

    # Add a second node and verify designer uniqueness
    main_sub_window.add_ao(OP_NODE_CLIPPER_FP, parameters={'num_channels': 1})
    make_all_sub_window_not_modified(window)
    node2 = main_sub_window.scene.nodes[1]
    assert node1.designator != node2.designator


# endregion

# region COMP_Combo_FP AO
def test_add_comp_combo_fp_ao_check_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()

    # Add the first node and verify the type
    main_sub_window.add_ao(OP_NODE_COMP_Combo_FP, parameters={'num_channels': 1})
    make_all_sub_window_not_modified(window)
    node1 = main_sub_window.scene.nodes[0]
    assert type(node1) == FlowNodeCompComboFP

    # Add a second node and verify designer uniqueness
    main_sub_window.add_ao(OP_NODE_COMP_Combo_FP, parameters={'num_channels': 1})
    make_all_sub_window_not_modified(window)
    node2 = main_sub_window.scene.nodes[1]
    assert node1.designator != node2.designator


# endregion

# region FIR_FP AO
def test_add_fir_fp_ao_check_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()

    # Add the first node and verify the type
    main_sub_window.add_ao(OP_NODE_FIR_FP, parameters={'num_channels': 1})
    make_all_sub_window_not_modified(window)
    node1 = main_sub_window.scene.nodes[0]
    assert type(node1) == FlowNodeFIRFP

    # Add a second node and verify designer uniqueness
    main_sub_window.add_ao(OP_NODE_FIR_FP, parameters={'num_channels': 1})
    make_all_sub_window_not_modified(window)
    node2 = main_sub_window.scene.nodes[1]
    assert node1.designator != node2.designator


# endregion

# region XOVER_FP AO
def test_add_xover_fp_ao_check_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()

    # Add the first node and verify the type
    main_sub_window.add_ao(OP_NODE_XOVER_FP)
    make_all_sub_window_not_modified(window)
    node1 = main_sub_window.scene.nodes[0]
    assert type(node1) == FlowNodeXOverFP

    # Add a second node and verify designer uniqueness
    main_sub_window.add_ao(OP_NODE_XOVER_FP)
    make_all_sub_window_not_modified(window)
    node2 = main_sub_window.scene.nodes[1]
    assert node1.designator != node2.designator


# endregion

# region LPF_FP AO
def test_add_lpf_fp_ao_check_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()

    # Add the first node and verify the type
    main_sub_window.add_ao(OP_NODE_LPF_FP, parameters={'num_channels': 1})
    make_all_sub_window_not_modified(window)
    node1 = main_sub_window.scene.nodes[0]
    assert type(node1) == FlowNodeLPFFP

    # Add a second node and verify designer uniqueness
    main_sub_window.add_ao(OP_NODE_LPF_FP, parameters={'num_channels': 1})
    make_all_sub_window_not_modified(window)
    node2 = main_sub_window.scene.nodes[1]
    assert node1.designator != node2.designator


# endregion

# region MUL_FP AO
def test_add_mul_fp_ao_check_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()

    # Add the first node and verify the type
    main_sub_window.add_ao(OP_NODE_MUL_FP)
    make_all_sub_window_not_modified(window)
    node1 = main_sub_window.scene.nodes[0]
    assert type(node1) == FlowNodeMulFP

    # Add a second node and verify designer uniqueness
    main_sub_window.add_ao(OP_NODE_MUL_FP)
    make_all_sub_window_not_modified(window)
    node2 = main_sub_window.scene.nodes[1]
    assert node1.designator != node2.designator

# endregion

# region SQRT_FP AO
def test_add_sqrt_fp_ao_check_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()

    # Add the first node and verify the type
    main_sub_window.add_ao(OP_NODE_SQRT_FP)
    make_all_sub_window_not_modified(window)
    node1 = main_sub_window.scene.nodes[0]
    assert type(node1) == FlowNodeSqrtFP

    # Add a second node and verify designer uniqueness
    main_sub_window.add_ao(OP_NODE_SQRT_FP)
    make_all_sub_window_not_modified(window)
    node2 = main_sub_window.scene.nodes[1]
    assert node1.designator != node2.designator


# endregion


# region ADDER_FP AO
def test_add_adder_fp_ao_check_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()

    # Add the first node and verify the type
    main_sub_window.add_ao(OP_NODE_ADDER_FP)
    make_all_sub_window_not_modified(window)
    node1 = main_sub_window.scene.nodes[0]
    assert type(node1) == FlowNodeAdderFP

    # Add a second node and verify designer uniqueness
    main_sub_window.add_ao(OP_NODE_ADDER_FP)
    make_all_sub_window_not_modified(window)
    node2 = main_sub_window.scene.nodes[1]
    assert node1.designator != node2.designator


# endregion

# region VISUALIZER AO
def test_add_visualizer_ao_check_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()

    # Add the first node and verify the type
    main_sub_window.add_ao(OP_NODE_VISUALIZER)
    make_all_sub_window_not_modified(window)
    node1 = main_sub_window.scene.nodes[0]
    assert type(node1) == FLOW_Node_VISUALIZER

    # Add a second node and verify designer uniqueness
    main_sub_window.add_ao(OP_NODE_VISUALIZER)
    make_all_sub_window_not_modified(window)
    node2 = main_sub_window.scene.nodes[1]
    assert node1.designator != node2.designator


# endregion

# region DUMP AO
def test_add_dump_ao_check_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()

    # Add the first node and verify the type
    main_sub_window.add_ao(OP_NODE_DUMP)
    make_all_sub_window_not_modified(window)
    node1 = main_sub_window.scene.nodes[0]
    assert type(node1) == FLOW_Node_DUMP

    # Add a second node and verify designer uniqueness
    main_sub_window.add_ao(OP_NODE_DUMP)
    make_all_sub_window_not_modified(window)
    node2 = main_sub_window.scene.nodes[1]
    assert node1.designator != node2.designator


# endregion


# region IN AO
def test_add_in_ao_check_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()

    # Add the first node and verify the type
    main_sub_window.add_ao(OP_NODE_ADC)
    make_all_sub_window_not_modified(window)
    node1 = main_sub_window.scene.nodes[0]
    assert type(node1) == FLOW_Node_IN

    # Add a second node and verify designer uniqueness
    main_sub_window.add_ao(OP_NODE_ADC)
    make_all_sub_window_not_modified(window)
    node2 = main_sub_window.scene.nodes[1]
    assert node1.designator != node2.designator


# endregion

# region OUT AO
def test_add_out_ao_check_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()

    # Add the first node and verify the type
    main_sub_window.add_ao(OP_NODE_DAC)
    make_all_sub_window_not_modified(window)
    node1 = main_sub_window.scene.nodes[0]
    assert type(node1) == FLOW_Node_OUT

    # Add a second node and verify designer uniqueness
    main_sub_window.add_ao(OP_NODE_DAC)
    make_all_sub_window_not_modified(window)
    node2 = main_sub_window.scene.nodes[1]
    assert node1.designator != node2.designator


# endregion

# region WAVPLAYER AO
def test_add_wav_player_ao_check_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()

    # Add the first node and verify the type
    main_sub_window.add_ao(OP_NODE_WAVPLAYER)
    make_all_sub_window_not_modified(window)
    node1 = main_sub_window.scene.nodes[0]
    assert type(node1) == FLOW_Node_WAVPLAYER

    # Add a second node and verify designer uniqueness
    main_sub_window.add_ao(OP_NODE_WAVPLAYER)
    make_all_sub_window_not_modified(window)
    node2 = main_sub_window.scene.nodes[1]
    assert node1.designator != node2.designator


# endregion
# region TONEGEN AO
def test_add_tone_gen_ao_check_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()

    # Add the first node and verify the type
    main_sub_window.add_ao(OP_NODE_TONEGEN)
    make_all_sub_window_not_modified(window)
    node1 = main_sub_window.scene.nodes[0]
    assert type(node1) == FLOW_Node_TONEGEN

    # Add a second node and verify designer uniqueness
    main_sub_window.add_ao(OP_NODE_TONEGEN)
    make_all_sub_window_not_modified(window)
    node2 = main_sub_window.scene.nodes[1]
    assert node1.designator != node2.designator


# endregion
# region NOISEGEN
def test_add_noise_gen_ao_check_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()

    # Add the first node and verify the type
    main_sub_window.add_ao(OP_NODE_NOISEGEN)
    make_all_sub_window_not_modified(window)
    node1 = main_sub_window.scene.nodes[0]
    assert type(node1) == FLOW_Node_NOISEGEN

    # Add a second node and verify designer uniqueness
    main_sub_window.add_ao(OP_NODE_NOISEGEN)
    make_all_sub_window_not_modified(window)
    node2 = main_sub_window.scene.nodes[1]
    assert node1.designator != node2.designator


# endregion

# region CHIRP
def test_add_chirp_ao_check_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()

    # Add the first node and verify the type
    main_sub_window.add_ao(OP_NODE_CHIRP)
    make_all_sub_window_not_modified(window)
    node1 = main_sub_window.scene.nodes[0]
    assert type(node1) == FLOW_Node_CHIRP

    # Add a second node and verify designer uniqueness
    main_sub_window.add_ao(OP_NODE_CHIRP)
    make_all_sub_window_not_modified(window)
    node2 = main_sub_window.scene.nodes[1]
    assert node1.designator != node2.designator


# endregion
# region ADDER
def test_add_adder_ao_check_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()

    # Add the first node and verify the type
    main_sub_window.add_ao(OP_NODE_ADDER)
    make_all_sub_window_not_modified(window)
    node1 = main_sub_window.scene.nodes[0]
    assert type(node1) == FLOW_Node_ADDER

    # Add a second node and verify designer uniqueness
    main_sub_window.add_ao(OP_NODE_ADDER)
    make_all_sub_window_not_modified(window)
    node2 = main_sub_window.scene.nodes[1]
    assert node1.designator != node2.designator


# endregion
# region NEGATOR
def test_add_negator_ao_check_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()

    # Add the first node and verify the type
    main_sub_window.add_ao(OP_NODE_NEGATOR)
    make_all_sub_window_not_modified(window)
    node1 = main_sub_window.scene.nodes[0]
    assert type(node1) == FLOW_Node_NEGATOR

    # Add a second node and verify designer uniqueness
    main_sub_window.add_ao(OP_NODE_NEGATOR)
    make_all_sub_window_not_modified(window)
    node2 = main_sub_window.scene.nodes[1]
    assert node1.designator != node2.designator


# endregion
# region ABS
def test_add_abs_ao_check_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()

    # Add the first node and verify the type
    main_sub_window.add_ao(OP_NODE_ABS)
    make_all_sub_window_not_modified(window)
    node1 = main_sub_window.scene.nodes[0]
    assert type(node1) == FLOW_Node_ABS

    # Add a second node and verify designer uniqueness
    main_sub_window.add_ao(OP_NODE_ABS)
    make_all_sub_window_not_modified(window)
    node2 = main_sub_window.scene.nodes[1]
    assert node1.designator != node2.designator


# endregion
# region SQRT
def test_add_sqrt_ao_check_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()

    # Add the first node and verify the type
    main_sub_window.add_ao(OP_NODE_SQRT)
    make_all_sub_window_not_modified(window)
    node1 = main_sub_window.scene.nodes[0]
    assert type(node1) == FLOW_Node_SQRT

    # Add a second node and verify designer uniqueness
    main_sub_window.add_ao(OP_NODE_SQRT)
    make_all_sub_window_not_modified(window)
    node2 = main_sub_window.scene.nodes[1]
    assert node1.designator != node2.designator


# endregion
# region MULTIPLIER
def test_add_multiplier_ao_check_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()

    # Add the first node and verify the type
    main_sub_window.add_ao(OP_NODE_MULTIPLIER)
    make_all_sub_window_not_modified(window)
    node1 = main_sub_window.scene.nodes[0]
    assert type(node1) == FLOW_Node_MULTIPLIER

    # Add a second node and verify designer uniqueness
    main_sub_window.add_ao(OP_NODE_MULTIPLIER)
    make_all_sub_window_not_modified(window)
    node2 = main_sub_window.scene.nodes[1]
    assert node1.designator != node2.designator


# endregion
# region SUBTRACTOR
def test_add_subtractor_ao_check_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()

    # Add the first node and verify the type
    main_sub_window.add_ao(OP_NODE_SUBTRACTOR)
    make_all_sub_window_not_modified(window)
    node1 = main_sub_window.scene.nodes[0]
    assert type(node1) == FLOW_Node_SUBTRACTOR

    # Add a second node and verify designer uniqueness
    main_sub_window.add_ao(OP_NODE_SUBTRACTOR)
    make_all_sub_window_not_modified(window)
    node2 = main_sub_window.scene.nodes[1]
    assert node1.designator != node2.designator


# endregion
# region BIQUAD
def test_add_biquad_ao_check_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()

    # Add the first node and verify the type
    main_sub_window.add_ao(OP_NODE_BIQUAD, parameters={'num_bands': 1, 'num_channels': 1, 'control': False})
    make_all_sub_window_not_modified(window)
    node1 = main_sub_window.scene.nodes[0]
    assert type(node1) == FLOW_Node_BIQUAD

    # Add a second node and verify designer uniqueness
    main_sub_window.add_ao(OP_NODE_BIQUAD, parameters={'num_bands': 1, 'num_channels': 1, 'control': False})
    make_all_sub_window_not_modified(window)
    node2 = main_sub_window.scene.nodes[1]
    assert node1.designator != node2.designator


# endregion
# region PEQ
def test_add_peq_ao_check_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()

    # Add the first node and verify the type
    main_sub_window.add_ao(OP_NODE_PEQ, parameters={'num_bands': 1, 'num_channels': 1, 'control': False})
    make_all_sub_window_not_modified(window)
    node1 = main_sub_window.scene.nodes[0]
    assert type(node1) == FLOW_Node_PEQ

    # Add a second node and verify designer uniqueness
    main_sub_window.add_ao(OP_NODE_PEQ, parameters={'num_bands': 1, 'num_channels': 1, 'control': False})
    make_all_sub_window_not_modified(window)
    node2 = main_sub_window.scene.nodes[1]
    assert node1.designator != node2.designator

    # Add PEQ containing 'Control'
    main_sub_window.add_ao(OP_NODE_PEQ, parameters={'num_bands': 1, 'num_channels': 1, 'control': True})
    make_all_sub_window_not_modified(window)
    node3 = main_sub_window.scene.nodes[2]
    assert node3.inctrls != []


# endregion
# region LPF
def test_add_lpf_ao_check_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()

    # Add the first node and verify the type
    main_sub_window.add_ao(OP_NODE_LPF, parameters={'num_channels': 1})
    make_all_sub_window_not_modified(window)
    node1 = main_sub_window.scene.nodes[0]
    assert type(node1) == FLOW_Node_LPF

    # Add a second node and verify designer uniqueness
    main_sub_window.add_ao(OP_NODE_LPF, parameters={'num_channels': 1})
    make_all_sub_window_not_modified(window)
    node2 = main_sub_window.scene.nodes[1]
    assert node1.designator != node2.designator


# endregion
# region HPF
def test_add_hpf_ao_check_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()

    # Add the first node and verify the type
    main_sub_window.add_ao(OP_NODE_HPF, parameters={'num_channels': 1})
    make_all_sub_window_not_modified(window)
    node1 = main_sub_window.scene.nodes[0]
    assert type(node1) == FLOW_Node_HPF

    # Add a second node and verify designer uniqueness
    main_sub_window.add_ao(OP_NODE_HPF, parameters={'num_channels': 1})
    make_all_sub_window_not_modified(window)
    node2 = main_sub_window.scene.nodes[1]
    assert node1.designator != node2.designator


# endregion
# region XOVER
def test_add_xover_ao_check_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()

    # Add the first node and verify the type
    main_sub_window.add_ao(OP_NODE_XOVER)
    make_all_sub_window_not_modified(window)
    node1 = main_sub_window.scene.nodes[0]
    assert type(node1) == FLOW_Node_XOVER

    # Add a second node and verify designer uniqueness
    main_sub_window.add_ao(OP_NODE_XOVER, parameters={'num_channels': 1})
    make_all_sub_window_not_modified(window)
    node2 = main_sub_window.scene.nodes[1]
    assert node1.designator != node2.designator


# endregion
# region IIRCOEF
def test_add_iircoef_ao_check_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()

    # Add the first node and verify the type
    main_sub_window.add_ao(OP_NODE_IIRCOEF, parameters={'num_channels': 1})
    make_all_sub_window_not_modified(window)
    node1 = main_sub_window.scene.nodes[0]
    assert type(node1) == FLOW_Node_IIRCOEF

    # Add a second node and verify designer uniqueness
    main_sub_window.add_ao(OP_NODE_IIRCOEF, parameters={'num_channels': 1})
    make_all_sub_window_not_modified(window)
    node2 = main_sub_window.scene.nodes[1]
    assert node1.designator != node2.designator


# endregion
# region FIR
def test_add_fir_ao_check_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()

    # Add the first node and verify the type
    main_sub_window.add_ao(OP_NODE_FIR, parameters={'num_channels': 1})
    make_all_sub_window_not_modified(window)
    node1 = main_sub_window.scene.nodes[0]
    assert type(node1) == FLOW_Node_FIR

    # Add a second node and verify designer uniqueness
    main_sub_window.add_ao(OP_NODE_FIR, parameters={'num_channels': 1})
    make_all_sub_window_not_modified(window)
    node2 = main_sub_window.scene.nodes[1]
    assert node1.designator != node2.designator


# endregion
# region GAIN
def test_add_gain_ao_check_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()

    # Add the first node and verify the type
    main_sub_window.add_ao(OP_NODE_GAIN, parameters={'num_channels': 1})
    make_all_sub_window_not_modified(window)
    node1 = main_sub_window.scene.nodes[0]
    assert type(node1) == FLOW_Node_GAIN

    # Add a second node and verify designer uniqueness
    main_sub_window.add_ao(OP_NODE_GAIN, parameters={'num_channels': 1})
    make_all_sub_window_not_modified(window)
    node2 = main_sub_window.scene.nodes[1]
    assert node1.designator != node2.designator


# endregion
# region SMART_GAIN
def test_add_smart_gain_ao_check_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()

    # Add the first node and verify the type
    main_sub_window.add_ao(OP_NODE_SMART_GAIN)
    make_all_sub_window_not_modified(window)
    node1 = main_sub_window.scene.nodes[0]
    assert type(node1) == FLOW_Node_SAMRT_GAIN

    # Add a second node and verify designer uniqueness
    main_sub_window.add_ao(OP_NODE_SMART_GAIN)
    make_all_sub_window_not_modified(window)
    node2 = main_sub_window.scene.nodes[1]
    assert node1.designator != node2.designator


# endregion
# region ATTEN
def test_add_atten_ao_check_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()

    # Add the first node and verify the type
    main_sub_window.add_ao(OP_NODE_ATTEN, parameters={'num_channels': 1})
    make_all_sub_window_not_modified(window)
    node1 = main_sub_window.scene.nodes[0]
    assert type(node1) == FLOW_Node_ATTEN

    # Add a second node and verify designer uniqueness
    main_sub_window.add_ao(OP_NODE_ATTEN, parameters={'num_channels': 1})
    make_all_sub_window_not_modified(window)
    node2 = main_sub_window.scene.nodes[1]
    assert node1.designator != node2.designator


# endregion
# region MUTE
def test_add_mute_ao_check_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()

    # Add the first node and verify the type
    main_sub_window.add_ao(OP_NODE_MUTE, parameters={'num_channels': 1})
    make_all_sub_window_not_modified(window)
    node1 = main_sub_window.scene.nodes[0]
    assert type(node1) == FLOW_Node_MUTE

    # Add a second node and verify designer uniqueness
    main_sub_window.add_ao(OP_NODE_MUTE, parameters={'num_channels': 1})
    make_all_sub_window_not_modified(window)
    node2 = main_sub_window.scene.nodes[1]
    assert node1.designator != node2.designator


# endregion
# region LOUDNESS
def test_add_loudness_ao_check_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()

    # Add the first node and verify the type
    main_sub_window.add_ao(OP_NODE_LOUDNESS)
    make_all_sub_window_not_modified(window)
    node1 = main_sub_window.scene.nodes[0]
    assert type(node1) == FLOW_Node_LOUDNESS

    # Add a second node and verify designer uniqueness
    main_sub_window.add_ao(OP_NODE_LOUDNESS)
    make_all_sub_window_not_modified(window)
    node2 = main_sub_window.scene.nodes[1]
    assert node1.designator != node2.designator


# endregion
# region POLARITY
def test_add_polarity_ao_check_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()

    # Add the first node and verify the type
    main_sub_window.add_ao(OP_NODE_POLARITY, parameters={'num_channels': 1})
    make_all_sub_window_not_modified(window)
    node1 = main_sub_window.scene.nodes[0]
    assert type(node1) == FLOW_Node_POLARITY

    # Add a second node and verify designer uniqueness
    main_sub_window.add_ao(OP_NODE_POLARITY, parameters={'num_channels': 1})
    make_all_sub_window_not_modified(window)
    node2 = main_sub_window.scene.nodes[1]
    assert node1.designator != node2.designator


# endregion
# region LIMITER
def test_add_limiter_ao_check_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()

    # Add the first node and verify the type
    main_sub_window.add_ao(OP_NODE_LIMITER, parameters={'num_channels': 1})
    make_all_sub_window_not_modified(window)
    node1 = main_sub_window.scene.nodes[0]
    assert type(node1) == FLOW_Node_LIMITER

    # Add a second node and verify designer uniqueness
    main_sub_window.add_ao(OP_NODE_LIMITER, parameters={'num_channels': 1})
    make_all_sub_window_not_modified(window)
    node2 = main_sub_window.scene.nodes[1]
    assert node1.designator != node2.designator


# endregion
# region LIMITER_MB
def test_add_limiter_mb_ao_check_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()

    # Add the first node and verify the type
    main_sub_window.add_ao(OP_NODE_LIMITER_MB)
    make_all_sub_window_not_modified(window)
    node1 = main_sub_window.scene.nodes[0]
    assert type(node1) == FLOW_Node_LIMITER_MB

    # Add a second node and verify designer uniqueness
    main_sub_window.add_ao(OP_NODE_LIMITER_MB)
    make_all_sub_window_not_modified(window)
    node2 = main_sub_window.scene.nodes[1]
    assert node1.designator != node2.designator


# endregion

# region COMP
def test_add_comp_ao_check_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()

    # Add the first node and verify the type
    main_sub_window.add_ao(OP_NODE_COMP, parameters={'num_channels': 1})
    make_all_sub_window_not_modified(window)
    node1 = main_sub_window.scene.nodes[0]
    assert type(node1) == FLOW_Node_COMP

    # Add a second node and verify designer uniqueness
    main_sub_window.add_ao(OP_NODE_COMP, parameters={'num_channels': 1})
    make_all_sub_window_not_modified(window)
    node2 = main_sub_window.scene.nodes[1]
    assert node1.designator != node2.designator


# endregion

# region COMP_Combo
def test_add_comp_combo_ao_check_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()

    # Add the first node and verify the type
    main_sub_window.add_ao(OP_NODE_COMP_Combo, parameters={'num_channels': 1})
    make_all_sub_window_not_modified(window)
    node1 = main_sub_window.scene.nodes[0]
    assert type(node1) == FLOW_Node_COMP_Combo

    # Add a second node and verify designer uniqueness
    main_sub_window.add_ao(OP_NODE_COMP_Combo, parameters={'num_channels': 1})
    make_all_sub_window_not_modified(window)
    node2 = main_sub_window.scene.nodes[1]
    assert node1.designator != node2.designator


# endregion
# region CLIPPER
def test_add_clipper_ao_check_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()

    # Add the first node and verify the type
    main_sub_window.add_ao(OP_NODE_CLIPPER, parameters={'num_channels': 1})
    make_all_sub_window_not_modified(window)
    node1 = main_sub_window.scene.nodes[0]
    assert type(node1) == FLOW_Node_CLIPPER

    # Add a second node and verify designer uniqueness
    main_sub_window.add_ao(OP_NODE_CLIPPER, parameters={'num_channels': 1})
    make_all_sub_window_not_modified(window)
    node2 = main_sub_window.scene.nodes[1]
    assert node1.designator != node2.designator


# endregion
# region GATE
def test_add_gate_ao_check_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()

    # Add the first node and verify the type
    main_sub_window.add_ao(OP_NODE_GATE, parameters={'num_channels': 1})
    make_all_sub_window_not_modified(window)
    node1 = main_sub_window.scene.nodes[0]
    assert type(node1) == FLOW_Node_GATE

    # Add a second node and verify designer uniqueness
    main_sub_window.add_ao(OP_NODE_GATE, parameters={'num_channels': 1})
    make_all_sub_window_not_modified(window)
    node2 = main_sub_window.scene.nodes[1]
    assert node1.designator != node2.designator


# endregion
# region SMART_GATE
def test_add_smart_gate_ao_check_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()

    # Add the first node and verify the type
    main_sub_window.add_ao(OP_NODE_SMART_GATE, parameters={'num_channels': 1})
    make_all_sub_window_not_modified(window)
    node1 = main_sub_window.scene.nodes[0]
    assert type(node1) == FLOW_Node_SMART_GATE

    # Add a second node and verify designer uniqueness
    main_sub_window.add_ao(OP_NODE_SMART_GATE, parameters={'num_channels': 1})
    make_all_sub_window_not_modified(window)
    node2 = main_sub_window.scene.nodes[1]
    assert node1.designator != node2.designator


# endregion
# region AUTO_COMP
def test_add_auto_comp_ao_check_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()

    # Add the first node and verify the type
    main_sub_window.add_ao(OP_NODE_AUTO_COMP, parameters={'num_channels': 1})
    make_all_sub_window_not_modified(window)
    node1 = main_sub_window.scene.nodes[0]
    assert type(node1) == FLOW_Node_AUTO_COMP

    # Add a second node and verify designer uniqueness
    main_sub_window.add_ao(OP_NODE_AUTO_COMP, parameters={'num_channels': 1})
    make_all_sub_window_not_modified(window)
    node2 = main_sub_window.scene.nodes[1]
    assert node1.designator != node2.designator


# endregion
# region MERGER
def test_add_merger_ao_check_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()

    # Add the first node and verify the type
    main_sub_window.add_ao(OP_NODE_MERGER)
    make_all_sub_window_not_modified(window)
    node1 = main_sub_window.scene.nodes[0]
    assert type(node1) == FLOW_Node_MERGER

    # Add a second node and verify designer uniqueness
    main_sub_window.add_ao(OP_NODE_MERGER)
    make_all_sub_window_not_modified(window)
    node2 = main_sub_window.scene.nodes[1]
    assert node1.designator != node2.designator


# endregion
# region MUX
def test_add_mux_ao_check_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()

    # Add the first node and verify the type
    main_sub_window.add_ao(OP_NODE_MUX, parameters={'num_out_channels': 1})
    make_all_sub_window_not_modified(window)
    node1 = main_sub_window.scene.nodes[0]
    assert type(node1) == FLOW_Node_MUX

    # Add a second node and verify designer uniqueness
    main_sub_window.add_ao(OP_NODE_MUX, parameters={'num_out_channels': 1})
    make_all_sub_window_not_modified(window)
    node2 = main_sub_window.scene.nodes[1]
    assert node1.designator != node2.designator


# endregion
# region DRYWET
def test_add_drywet_ao_check_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()

    # Add the first node and verify the type
    main_sub_window.add_ao(OP_NODE_DRYWET)
    make_all_sub_window_not_modified(window)
    node1 = main_sub_window.scene.nodes[0]
    assert type(node1) == FLOW_Node_DRYWET

    # Add a second node and verify designer uniqueness
    main_sub_window.add_ao(OP_NODE_DRYWET)
    make_all_sub_window_not_modified(window)
    node2 = main_sub_window.scene.nodes[1]
    assert node1.designator != node2.designator


# endregion
# region MIXER
def test_add_mixer_ao_check_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()

    # Add the first node and verify the type
    main_sub_window.add_ao(OP_NODE_MIXER, parameters={'num_in_channels': 1, 'num_out_channels': 1})
    make_all_sub_window_not_modified(window)
    node1 = main_sub_window.scene.nodes[0]
    assert type(node1) == FLOW_Node_MIXER

    # Add a second node and verify designer uniqueness
    main_sub_window.add_ao(OP_NODE_MIXER, parameters={'num_in_channels': 1, 'num_out_channels': 1})
    make_all_sub_window_not_modified(window)
    node2 = main_sub_window.scene.nodes[1]
    assert node1.designator != node2.designator


# endregion
# region DELAY
def test_add_delay_ao_check_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()

    # Add the first node and verify the type
    main_sub_window.add_ao(OP_NODE_DELAY, parameters={'num_channels': 1})
    make_all_sub_window_not_modified(window)
    node1 = main_sub_window.scene.nodes[0]
    assert type(node1) == FLOW_Node_DELAY

    # Add a second node and verify designer uniqueness
    main_sub_window.add_ao(OP_NODE_DELAY, parameters={'num_channels': 1})
    make_all_sub_window_not_modified(window)
    node2 = main_sub_window.scene.nodes[1]
    assert node1.designator != node2.designator


# endregion
# region DELAY_Intp
def test_add_delay_intp_ao_check_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()

    # Add the first node and verify the type
    main_sub_window.add_ao(OP_NODE_DELAY_Intp)
    make_all_sub_window_not_modified(window)
    node1 = main_sub_window.scene.nodes[0]
    assert type(node1) == FLOW_Node_DELAY_Intp

    # Add a second node and verify designer uniqueness
    main_sub_window.add_ao(OP_NODE_DELAY_Intp)
    make_all_sub_window_not_modified(window)
    node2 = main_sub_window.scene.nodes[1]
    assert node1.designator != node2.designator


# endregion
# region MULTITAP
def test_add_multitap_ao_check_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()

    # Add the first node and verify the type
    main_sub_window.add_ao(OP_NODE_MULTITAP, parameters={'num_taps': 1})
    make_all_sub_window_not_modified(window)
    node1 = main_sub_window.scene.nodes[0]
    assert type(node1) == FLOW_Node_MULTITAP

    # Add a second node and verify designer uniqueness
    main_sub_window.add_ao(OP_NODE_MULTITAP, parameters={'num_taps': 1})
    make_all_sub_window_not_modified(window)
    node2 = main_sub_window.scene.nodes[1]
    assert node1.designator != node2.designator


# endregion
# region LONG_APF
def test_add_long_apf_ao_check_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()

    # Add the first node and verify the type
    main_sub_window.add_ao(OP_NODE_LONG_APF, parameters={'num_taps': 1})
    make_all_sub_window_not_modified(window)
    node1 = main_sub_window.scene.nodes[0]
    assert type(node1) == FLOW_Node_LONG_APF

    # Add a second node and verify designer uniqueness
    main_sub_window.add_ao(OP_NODE_LONG_APF, parameters={'num_taps': 1})
    make_all_sub_window_not_modified(window)
    node2 = main_sub_window.scene.nodes[1]
    assert node1.designator != node2.designator


# endregion
# region LPF_COMB_FILTER
def test_add_lpf_comb_filter_ao_check_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()

    # Add the first node and verify the type
    main_sub_window.add_ao(OP_NODE_LPF_COMB_FILTER, parameters={'num_taps': 1})
    make_all_sub_window_not_modified(window)
    node1 = main_sub_window.scene.nodes[0]
    assert type(node1) == FLOW_Node_LPF_COMB_FILTER

    # Add a second node and verify designer uniqueness
    main_sub_window.add_ao(OP_NODE_LPF_COMB_FILTER, parameters={'num_taps': 1})
    make_all_sub_window_not_modified(window)
    node2 = main_sub_window.scene.nodes[1]
    assert node1.designator != node2.designator


# endregion
# region REVERB
# def test_add_reverb_ao_check_ao_in_scene(window):
#     window.onFileNew()
#     main_sub_window = window.findMain().widget()
#     main_sub_window.add_ao(OP_NODE_REVERB)
#     make_all_sub_window_not_modified(window)
#     assert type(main_sub_window.scene.nodes[0]) == FLOW_Node_REVERB
# def test_add_two_reverb_ao_check_designator_different(window):
#     window.onFileNew()
#     main_sub_window = window.findMain().widget()
#     main_sub_window.add_ao(OP_NODE_REVERB)
#     main_sub_window.add_ao(OP_NODE_REVERB)
#     make_all_sub_window_not_modified(window)
#     assert main_sub_window.scene.nodes[0].designator != main_sub_window.scene.nodes[1].designator
# endregion


# region REVERB_V2
def test_add_reverb_v2_ao_check_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()

    # Add the first node and verify the type
    main_sub_window.add_ao(OP_NODE_REVERB_V2)
    make_all_sub_window_not_modified(window)
    node1 = main_sub_window.scene.nodes[0]
    assert type(node1) == FLOW_Node_REVERB_V2

    # Add a second node and verify designer uniqueness
    main_sub_window.add_ao(OP_NODE_REVERB_V2)
    make_all_sub_window_not_modified(window)
    node2 = main_sub_window.scene.nodes[1]
    assert node1.designator != node2.designator


# endregion
# region REVERB_V2


# endregion
# region IR
def test_add_ir_ao_check_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()

    # Add the first node and verify the type
    main_sub_window.add_ao(OP_NODE_IR)
    make_all_sub_window_not_modified(window)
    node1 = main_sub_window.scene.nodes[0]
    assert type(node1) == FLOW_Node_IR

    # Add a second node and verify designer uniqueness
    main_sub_window.add_ao(OP_NODE_IR)
    make_all_sub_window_not_modified(window)
    node2 = main_sub_window.scene.nodes[1]
    assert node1.designator != node2.designator


# endregion
# region IR_ST
# def test_add_ir_st_ao_check_ao_in_scene(window):
#     window.onFileNew()
#     main_sub_window = window.findMain().widget()
#     main_sub_window.add_ao(OP_NODE_IR_ST)
#     make_all_sub_window_not_modified(window)
#     assert type(main_sub_window.scene.nodes[0]) == FLOW_Node_IR_ST
#
#
# def test_add_two_ir_st_ao_check_designator_different(window):
#     window.onFileNew()
#     main_sub_window = window.findMain().widget()
#     main_sub_window.add_ao(OP_NODE_IR_ST)
#     main_sub_window.add_ao(OP_NODE_IR_ST)
#     make_all_sub_window_not_modified(window)
#     assert main_sub_window.scene.nodes[0].designator != main_sub_window.scene.nodes[1].designator
# endregion
# region CHORUS


def test_add_chorus_ao_check_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()

    # Add the first node and verify the type
    main_sub_window.add_ao(OP_NODE_CHORUS)
    make_all_sub_window_not_modified(window)
    node1 = main_sub_window.scene.nodes[0]
    assert type(node1) == FLOW_Node_CHORUS

    # Add a second node and verify designer uniqueness
    main_sub_window.add_ao(OP_NODE_CHORUS)
    make_all_sub_window_not_modified(window)
    node2 = main_sub_window.scene.nodes[1]
    assert node1.designator != node2.designator


# endregion
# region CROSSFEED
def test_add_crossfeed_ao_check_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()

    # Add the first node and verify the type
    main_sub_window.add_ao(OP_NODE_CROSSFEED)
    make_all_sub_window_not_modified(window)
    node1 = main_sub_window.scene.nodes[0]
    assert type(node1) == FLOW_Node_CROSSFEED

    # Add a second node and verify designer uniqueness
    main_sub_window.add_ao(OP_NODE_CROSSFEED)
    make_all_sub_window_not_modified(window)
    node2 = main_sub_window.scene.nodes[1]
    assert node1.designator != node2.designator


# endregion
# region VAD
def test_add_vad_ao_check_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()

    # Add the first node and verify the type
    main_sub_window.add_ao(OP_NODE_VAD)
    make_all_sub_window_not_modified(window)
    node1 = main_sub_window.scene.nodes[0]
    assert type(node1) == FLOW_Node_VAD

    # Add a second node and verify designer uniqueness
    main_sub_window.add_ao(OP_NODE_VAD)
    make_all_sub_window_not_modified(window)
    node2 = main_sub_window.scene.nodes[1]
    assert node1.designator != node2.designator


# endregion
# region DBASS
def test_add_dbass_ao_check_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()

    # Add the first node and verify the type
    main_sub_window.add_ao(OP_NODE_DBASS, parameters={'num_channels': 1})
    make_all_sub_window_not_modified(window)
    node1 = main_sub_window.scene.nodes[0]
    assert type(node1) == FLOW_Node_DBASS

    # Add a second node and verify designer uniqueness
    main_sub_window.add_ao(OP_NODE_DBASS, parameters={'num_channels': 1})
    make_all_sub_window_not_modified(window)
    node2 = main_sub_window.scene.nodes[1]
    assert node1.designator != node2.designator


# endregion
# region DEESSER
def test_add_deesser_ao_check_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()

    # Add the first node and verify the type
    main_sub_window.add_ao(OP_NODE_DEESSER, parameters={'num_channels': 1})
    make_all_sub_window_not_modified(window)
    node1 = main_sub_window.scene.nodes[0]
    assert type(node1) == FLOW_Node_DEESSER

    # Add a second node and verify designer uniqueness
    main_sub_window.add_ao(OP_NODE_DEESSER, parameters={'num_channels': 1})
    make_all_sub_window_not_modified(window)
    node2 = main_sub_window.scene.nodes[1]
    assert node1.designator != node2.designator


# endregion
# region VBASS
def test_add_vbass_ao_check_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()

    # Add the first node and verify the type
    main_sub_window.add_ao(OP_NODE_VBASS, parameters={'num_channels': 1})
    make_all_sub_window_not_modified(window)
    node1 = main_sub_window.scene.nodes[0]
    assert type(node1) == FLOW_Node_VBASS

    # Add a second node and verify designer uniqueness
    main_sub_window.add_ao(OP_NODE_VBASS, parameters={'num_channels': 1})
    make_all_sub_window_not_modified(window)
    node2 = main_sub_window.scene.nodes[1]
    assert node1.designator != node2.designator


# endregion
# region AGC
def test_add_agc_ao_check_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()

    # Add the first node and verify the type
    main_sub_window.add_ao(OP_NODE_AGC, parameters={'num_channels': 1})
    make_all_sub_window_not_modified(window)
    node1 = main_sub_window.scene.nodes[0]
    assert type(node1) == FLOW_Node_AGC

    # Add a second node and verify designer uniqueness
    main_sub_window.add_ao(OP_NODE_AGC, parameters={'num_channels': 1})
    make_all_sub_window_not_modified(window)
    node2 = main_sub_window.scene.nodes[1]
    assert node1.designator != node2.designator


# endregion
# region DLOUDNESS
def test_add_dloudness_ao_check_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()

    # Add the first node and verify the type
    main_sub_window.add_ao(OP_NODE_DLOUDNESS, parameters={'num_channels': 1})
    make_all_sub_window_not_modified(window)
    node1 = main_sub_window.scene.nodes[0]
    assert type(node1) == FLOW_Node_DLOUDNESS

    # Add a second node and verify designer uniqueness
    main_sub_window.add_ao(OP_NODE_DLOUDNESS, parameters={'num_channels': 1})
    make_all_sub_window_not_modified(window)
    node2 = main_sub_window.scene.nodes[1]
    assert node1.designator != node2.designator


# endregion
# region BEAMFORMING
def test_add_beamforming_ao_check_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()

    # Add the first node and verify the type
    main_sub_window.add_ao(OP_NODE_BEAMFORMING)
    make_all_sub_window_not_modified(window)
    node1 = main_sub_window.scene.nodes[0]
    assert type(node1) == FLOW_Node_BEAMFORMING

    # Add a second node and verify designer uniqueness
    main_sub_window.add_ao(OP_NODE_BEAMFORMING)
    make_all_sub_window_not_modified(window)
    node2 = main_sub_window.scene.nodes[1]
    assert node1.designator != node2.designator


# endregion
# region BEAMFORMING_2ch
def test_add_beamforming_2ch_ao_check_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()

    # Add the first node and verify the type
    main_sub_window.add_ao(OP_NODE_BEAMFORMING_2ch)
    make_all_sub_window_not_modified(window)
    node1 = main_sub_window.scene.nodes[0]
    assert type(node1) == FLOW_Node_BEAMFORMING_2ch

    # Add a second node and verify designer uniqueness
    main_sub_window.add_ao(OP_NODE_BEAMFORMING_2ch)
    make_all_sub_window_not_modified(window)
    node2 = main_sub_window.scene.nodes[1]
    assert node1.designator != node2.designator


# endregion
# region BEAMFORMING_3ch
def test_add_beamforming_3ch_ao_check_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()

    # Add the first node and verify the type
    main_sub_window.add_ao(OP_NODE_BEAMFORMING_3ch)
    make_all_sub_window_not_modified(window)
    node1 = main_sub_window.scene.nodes[0]
    assert type(node1) == FLOW_Node_BEAMFORMING_3ch

    # Add a second node and verify designer uniqueness
    main_sub_window.add_ao(OP_NODE_BEAMFORMING_3ch)
    make_all_sub_window_not_modified(window)
    node2 = main_sub_window.scene.nodes[1]
    assert node1.designator != node2.designator


# endregion
# region VAD_IABSE
def test_add_vad_iabse_ao_check_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()

    # Add the first node and verify the type
    main_sub_window.add_ao(OP_NODE_VAD_IABSE)
    make_all_sub_window_not_modified(window)
    node1 = main_sub_window.scene.nodes[0]
    assert type(node1) == FLOW_Node_VAD_IABSE

    # Add a second node and verify designer uniqueness
    main_sub_window.add_ao(OP_NODE_VAD_IABSE)
    make_all_sub_window_not_modified(window)
    node2 = main_sub_window.scene.nodes[1]
    assert node1.designator != node2.designator


# endregion
# region AEC
def test_add_aec_ao_check_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()

    # Add the first node and verify the type
    main_sub_window.add_ao(OP_NODE_AEC)
    make_all_sub_window_not_modified(window)
    node1 = main_sub_window.scene.nodes[0]
    assert type(node1) == FLOW_Node_AEC

    # Add a second node and verify designer uniqueness
    main_sub_window.add_ao(OP_NODE_AEC)
    make_all_sub_window_not_modified(window)
    node2 = main_sub_window.scene.nodes[1]
    assert node1.designator != node2.designator


# endregion
# region AI_NR
def test_add_ai_nr_ao_check_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()

    # Add the first node and verify the type
    main_sub_window.add_ao(OP_NODE_AI_NR)
    make_all_sub_window_not_modified(window)
    node1 = main_sub_window.scene.nodes[0]
    assert type(node1) == FLOW_Node_AI_NR

    # Add a second node and verify designer uniqueness
    main_sub_window.add_ao(OP_NODE_AI_NR)
    make_all_sub_window_not_modified(window)
    node2 = main_sub_window.scene.nodes[1]
    assert node1.designator != node2.designator


# endregion
# region NOISEREDUCTION
def test_add_noise_reduction_ao_check_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()

    # Add the first node and verify the type
    main_sub_window.add_ao(OP_NODE_NOISEREDUCTION)
    make_all_sub_window_not_modified(window)
    node1 = main_sub_window.scene.nodes[0]
    assert type(node1) == FLOW_Node_NOISEREDCUTION

    # Add a second node and verify designer uniqueness
    main_sub_window.add_ao(OP_NODE_NOISEREDUCTION)
    make_all_sub_window_not_modified(window)
    node2 = main_sub_window.scene.nodes[1]
    assert node1.designator != node2.designator


# endregion
# region SPATIALIZER
def test_add_spatializer_ao_check_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()

    # Add the first node and verify the type
    main_sub_window.add_ao(OP_NODE_SPATIALIZER)
    make_all_sub_window_not_modified(window)
    node1 = main_sub_window.scene.nodes[0]
    assert type(node1) == FLOW_Node_SPATIALIZER

    # Add a second node and verify designer uniqueness
    main_sub_window.add_ao(OP_NODE_SPATIALIZER)
    make_all_sub_window_not_modified(window)
    node2 = main_sub_window.scene.nodes[1]
    assert node1.designator != node2.designator


# endregion
# region SUBPATCH
def test_add_subpatch_ao_check_ao_in_scene(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    main_sub_window.add_ao(OP_NODE_SUBPATCH, parameters={'num_in_channels': 1, 'num_out_channels': 1})
    make_all_sub_window_not_modified(window)
    assert type(main_sub_window.scene.nodes[0]) == FLOW_Node_SUBPATCH


def test_add_subpatch_ao_check_new_sub_window_exist(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    main_sub_window.add_ao(OP_NODE_SUBPATCH, parameters={'num_in_channels': 1, 'num_out_channels': 1})
    make_all_sub_window_not_modified(window)
    assert len(window.mdiArea.subWindowList()) == 2


def test_add_two_subpatch_ao_check_designator_different(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()
    main_sub_window.add_ao(OP_NODE_SUBPATCH, parameters={'num_in_channels': 1, 'num_out_channels': 1})
    main_sub_window.add_ao(OP_NODE_SUBPATCH, parameters={'num_in_channels': 1, 'num_out_channels': 1})
    make_all_sub_window_not_modified(window)
    assert main_sub_window.scene.nodes[0].designator != main_sub_window.scene.nodes[1].designator


# endregion
# region METER
def test_add_meter_ao_check_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()

    # Add the first node and verify the type
    main_sub_window.add_ao(OP_NODE_METER, parameters={'num_channels': 1})
    make_all_sub_window_not_modified(window)
    node1 = main_sub_window.scene.nodes[0]
    assert type(node1) == FLOW_Node_METER

    # Add a second node and verify designer uniqueness
    main_sub_window.add_ao(OP_NODE_METER, parameters={'num_channels': 1})
    make_all_sub_window_not_modified(window)
    node2 = main_sub_window.scene.nodes[1]
    assert node1.designator != node2.designator


# endregion
# region SPECTRUM
def test_add_spectrum_ao_check_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()

    # Add the first node and verify the type
    main_sub_window.add_ao(OP_NODE_SPECTRUM)
    make_all_sub_window_not_modified(window)
    node1 = main_sub_window.scene.nodes[0]
    assert type(node1) == FLOW_Node_SPECTRUM

    # Add a second node and verify designer uniqueness
    main_sub_window.add_ao(OP_NODE_SPECTRUM)
    make_all_sub_window_not_modified(window)
    node2 = main_sub_window.scene.nodes[1]
    assert node1.designator != node2.designator


# endregion
# region RTA
def test_add_rta_ao_check_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()

    # Add the first node and verify the type
    main_sub_window.add_ao(OP_NODE_RTA)
    make_all_sub_window_not_modified(window)
    node1 = main_sub_window.scene.nodes[0]
    assert type(node1) == FLOW_Node_RTA

    # Add a second node and verify designer uniqueness
    main_sub_window.add_ao(OP_NODE_RTA)
    make_all_sub_window_not_modified(window)
    node2 = main_sub_window.scene.nodes[1]
    assert node1.designator != node2.designator


# endregion
# region COMMENT
def test_add_comment_ao_check_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()

    # Add the first node and verify the type
    main_sub_window.add_ao(OP_NODE_COMMENT)
    make_all_sub_window_not_modified(window)
    node1 = main_sub_window.scene.nodes[0]
    assert type(node1) == FLOW_Node_COMMENT

    # Add a second node and verify designer uniqueness
    main_sub_window.add_ao(OP_NODE_COMMENT)
    make_all_sub_window_not_modified(window)
    node2 = main_sub_window.scene.nodes[1]
    assert node1.designator != node2.designator


# endregion
# region IN_FP
def test_add_in_fp_ao_check_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()

    # Add the first node and verify the type
    main_sub_window.add_ao(OP_NODE_IN_FP)
    make_all_sub_window_not_modified(window)
    node1 = main_sub_window.scene.nodes[0]
    assert type(node1) == FLOW_Node_IN_FP

    # Add a second node and verify designer uniqueness
    main_sub_window.add_ao(OP_NODE_IN_FP)
    make_all_sub_window_not_modified(window)
    node2 = main_sub_window.scene.nodes[1]
    assert node1.designator != node2.designator


# endregion
# region OUT_FP
def test_add_out_fp_ao_check_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()

    # Add the first node and verify the type
    main_sub_window.add_ao(OP_NODE_OUT_FP)
    make_all_sub_window_not_modified(window)
    node1 = main_sub_window.scene.nodes[0]
    assert type(node1) == FLOW_Node_OUT_FP

    # Add a second node and verify designer uniqueness
    main_sub_window.add_ao(OP_NODE_OUT_FP)
    make_all_sub_window_not_modified(window)
    node2 = main_sub_window.scene.nodes[1]
    assert node1.designator != node2.designator


# endregion
# region HPF_FP
def test_add_hpf_fp_ao_check_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()

    # Add the first node and verify the type
    main_sub_window.add_ao(OP_NODE_HPF_FP, parameters={'num_channels': 1})
    make_all_sub_window_not_modified(window)
    node1 = main_sub_window.scene.nodes[0]
    assert type(node1) == FLOW_Node_HPF_FP

    # Add a second node and verify designer uniqueness
    main_sub_window.add_ao(OP_NODE_HPF_FP, parameters={'num_channels': 1})
    make_all_sub_window_not_modified(window)
    node2 = main_sub_window.scene.nodes[1]
    assert node1.designator != node2.designator


# endregion
# region PEQ_FP
def test_add_peq_fp_ao_check_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()

    # Add the first node and verify the type
    main_sub_window.add_ao(OP_NODE_PEQ_FP, parameters={'num_bands': 1, 'num_channels': 1, 'control': False})
    make_all_sub_window_not_modified(window)
    node1 = main_sub_window.scene.nodes[0]
    assert type(node1) == FLOW_Node_PEQ_FP

    # Add a second node and verify designer uniqueness
    main_sub_window.add_ao(OP_NODE_PEQ_FP, parameters={'num_bands': 1, 'num_channels': 1, 'control': False})
    make_all_sub_window_not_modified(window)
    node2 = main_sub_window.scene.nodes[1]
    assert node1.designator != node2.designator


# endregion
# region ABS_FP
def test_add_abs_fp_ao_check_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()

    # Add the first node and verify the type
    main_sub_window.add_ao(OP_NODE_ABS_FP)
    make_all_sub_window_not_modified(window)
    node1 = main_sub_window.scene.nodes[0]
    assert type(node1) == FLOW_Node_ABS_FP

    # Add a second node and verify designer uniqueness
    main_sub_window.add_ao(OP_NODE_ABS_FP)
    make_all_sub_window_not_modified(window)
    node2 = main_sub_window.scene.nodes[1]
    assert node1.designator != node2.designator


# endregion
# region COMP_FP
def test_add_comp_fp_ao_check_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()

    # Add the first node and verify the type
    main_sub_window.add_ao(OP_NODE_COMP_FP, parameters={'num_channels': 1})
    make_all_sub_window_not_modified(window)
    node1 = main_sub_window.scene.nodes[0]
    assert type(node1) == FLOW_Node_COMP_FP

    # Add a second node and verify designer uniqueness
    main_sub_window.add_ao(OP_NODE_COMP_FP, parameters={'num_channels': 1})
    make_all_sub_window_not_modified(window)
    node2 = main_sub_window.scene.nodes[1]
    assert node1.designator != node2.designator


# endregion
# region LIMITER_FP
def test_add_limiter_fp_ao_check_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()

    # Add the first node and verify the type
    main_sub_window.add_ao(OP_NODE_LIMITER_FP, parameters={'num_channels': 1})
    make_all_sub_window_not_modified(window)
    node1 = main_sub_window.scene.nodes[0]
    assert type(node1) == FLOW_Node_LIMITER_FP

    # Add a second node and verify designer uniqueness
    main_sub_window.add_ao(OP_NODE_LIMITER_FP, parameters={'num_channels': 1})
    make_all_sub_window_not_modified(window)
    node2 = main_sub_window.scene.nodes[1]
    assert node1.designator != node2.designator


# endregion
# region METER_FP
def test_add_meter_fp_ao_check_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()

    # Add the first node and verify the type
    main_sub_window.add_ao(OP_NODE_METER_FP, parameters={'num_channels': 1})
    make_all_sub_window_not_modified(window)
    node1 = main_sub_window.scene.nodes[0]
    assert type(node1) == FLOW_Node_METER_FP

    # Add a second node and verify designer uniqueness
    main_sub_window.add_ao(OP_NODE_METER_FP, parameters={'num_channels': 1})
    make_all_sub_window_not_modified(window)
    node2 = main_sub_window.scene.nodes[1]
    assert node1.designator != node2.designator


# endregion
# region MUX_FP
def test_add_mux_fp_ao_check_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()

    # Add the first node and verify the type
    main_sub_window.add_ao(OP_NODE_MUX_FP, parameters={'num_out_channels': 1})
    make_all_sub_window_not_modified(window)
    node1 = main_sub_window.scene.nodes[0]
    assert type(node1) == FLOW_Node_MUX_FP

    # Add a second node and verify designer uniqueness
    main_sub_window.add_ao(OP_NODE_MUX_FP, parameters={'num_out_channels': 1})
    make_all_sub_window_not_modified(window)
    node2 = main_sub_window.scene.nodes[1]
    assert node1.designator != node2.designator


# endregion
# region MUTE_FP
def test_add_mute_fp_ao_check_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()

    # Add the first node and verify the type
    main_sub_window.add_ao(OP_NODE_MUTE_FP)
    make_all_sub_window_not_modified(window)
    node1 = main_sub_window.scene.nodes[0]
    assert type(node1) == FLOW_Node_MUTE_FP

    # Add a second node and verify designer uniqueness
    main_sub_window.add_ao(OP_NODE_MUTE_FP)
    make_all_sub_window_not_modified(window)
    node2 = main_sub_window.scene.nodes[1]
    assert node1.designator != node2.designator


# endregion
# region GAIN_FP
def test_add_gain_fp_ao_check_ao(window):
    window.onFileNew()
    main_sub_window = window.findMain().widget()

    # Add the first node and verify the type
    main_sub_window.add_ao(OP_NODE_GAIN_FP, parameters={'num_channels': 1})
    make_all_sub_window_not_modified(window)
    node1 = main_sub_window.scene.nodes[0]
    assert type(node1) == FLOW_Node_GAIN_FP

    # Add a second node and verify designer uniqueness
    main_sub_window.add_ao(OP_NODE_GAIN_FP, parameters={'num_channels': 1})
    make_all_sub_window_not_modified(window)
    node2 = main_sub_window.scene.nodes[1]
    assert node1.designator != node2.designator
# endregion
