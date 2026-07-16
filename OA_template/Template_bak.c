#include "CAOTemplate.h"


static void CAOTemplate_Process(CAudioObject* me, const void* in, void* out, int frameSize);
static int CAOTemplate_Prepare(CAudioObject* me, float sampleRate, int frameSize);
static void CAOTemplate_Release(CAudioObject* me);
static void CAOTemplate_Destroy(CAudioObject* me);
static void CAOTemplate_AOTemplateChangeHandler(CParam* param, float newValue, int row, int column);

// BEGIN: AUTO GEN INIT PARAM CODE
// declare parameter info for parameter initialization data

// END: AUTO GEN INIT PARAM CODE 

FLOW_API OPT_OS CAOTemplate* CAOTemplate_New(void* addr, const char* instanceName, int numInChannels, int numOutChannels)
{

	if (addr == NULL)
	{
		return NULL;
	}

	CAOTemplate* me = addr;

	/* initialize or construct any variable or object here*/	
	me->_channels = numInChannels;
	/* USER CODE BEGIN init */

	/* USER CODE END init */
	/* The CAudioObject must construct first, because every AO is inherit from it */
	me->cao_base = New(CAudioObject, numInChannels, numOutChannels);	
	me->cao_base->_DerivedObj = me; // TODO: update _DerivedObj member for later data access
	me->cao_base->_isFxp = false;
	/* set audio object's instance name and type name */
	me->cao_base->SetInstanceName(me->cao_base, instanceName);
	me->cao_base->SetTypeName(me->cao_base, "AOTemplate");

	// BEGIN: AUTO GEN NEW PARAM CODE
	/* construct params and add to this audio object*/

	// END: AUTO GEN NEW PARAM CODE

	// BEGIN: AUTO GEN REGISTER HANDLER CODE
	/* register the parameters to their change handler*/

	// END: AUTO GEN REGISTER HANDLER CODE

	/* point your common CAudioObject method to this AO's static method here, 
	when using it, you need to access the CAudioObject base object first*/
	me->cao_base->Process = CAOTemplate_Process;
	me->cao_base->Prepare = CAOTemplate_Prepare;
	me->cao_base->Release = CAOTemplate_Release;
	me->cao_base->destroyWithParent = CAOTemplate_Destroy;

	return me;
}

FLOW_API OPT_OS void CAOTemplate_Delete(CAOTemplate* obj)
{
	if(obj->cao_base->_isPrepared)
	{
		CAOTemplate_Release(obj->cao_base);
	}

	// BEGIN: AUTO GEN FREE PARAM CODE
	// free parameter memory

	// END: AUTO GEN FREE PARAM CODE

	Delete(CAudioObject, obj->cao_base);
}



void CAOTemplate_Process(CAudioObject* me, const void* in, void* out, int frameSize)
{
	AudioBuffer* ins = (AudioBuffer*)in;
	AudioBuffer* outs = (AudioBuffer*)out;;
	CAOTemplate* This = me->_DerivedObj;
	int ch = This->_channels;

	// Your audio-processing code goes here!
	// For more details, see the help from example project 
	// Right now we are not producing any data, in which case we need to clear the buffer
	// (to prevent the output of random noise)
	/* USER CODE BEGIN Process */

	for (int channel = 0; channel < ch; ++channel)
	{
		float* inputs = ins->GetChannelData(ins, channel);
		float* outputs = outs->GetChannelData(outs, channel);
		
		memcpy(outputs, inputs, sizeof(float) * frameSize);
	}
	/* USER CODE END Process */

}

OPT_OS int CAOTemplate_Prepare(CAudioObject* me, float sampleRate, int frameSize)
{
	CAOTemplate* This = me->_DerivedObj;

	me->SetSampleRate(me, sampleRate);
	me->SetFrameSize(me, frameSize);
	
	// This function will be called when the audio device is started, or when
	// its settings (i.e. sample rate, block size, etc) are changed.
	// You can use this function to initialise any resources you might need,
	// For more details, see the help from example project 
	/* USER CODE BEGIN MemoryAllocate */
		
	/* USER CODE END MemoryAllocate */
	me->_isPrepared = 1;

	me->UpdateAllParamsToDefault(me);
	return 0;
}

OPT_OS void CAOTemplate_Release(CAudioObject* me)
{
	CAOTemplate* This = me->_DerivedObj;

	// This function will be called when the audio device is ended. 
	// You can use this function to release memory of resource.
	/* USER CODE BEGIN MemoryRelease */
	
	/* USER CODE END MemoryRelease */	
	me->_isPrepared = 0;
}

OPT_OS void CAOTemplate_Destroy(CAudioObject* me)
{
	CAOTemplate* This = me->_DerivedObj;
	CAOTemplate_Delete(This);
	flow_free(This);
}

OPT_OS void CAOTemplate_AOTemplateChangeHandler(CParam* param, float newValue, int row, int column)
{
	int ch = column;
	CAOTemplate* This = param->_Owner;
	
	// This handler function handle the parameter change action, needs to register handler in the beginning of file
	// For more details, see the help from example project 
	/* USER CODE BEGIN ParamHandler */

	/* USER CODE END ParamHandler */
}



//---------------------- below is creator implementation ------------------------------------

FLOW_API OPT_OS CAudioObject* AOTemplateCreator_CreateAudioObject(const char* instanceName, unsigned int numInChannels, unsigned int numOutChannels, struct hashmap_s paramList)
{

	CAOTemplate* AOTemplateCreated = New(CAOTemplate, instanceName, numInChannels, numOutChannels);
	return AOTemplateCreated->cao_base;
}


FLOW_API OPT_OS void AOTemplateCreator_parseParam(CAudioObject* obj, struct hashmap_s paramList)
{
	parseAndSetAllParam(obj, paramList);
}
