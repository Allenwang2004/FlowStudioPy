#pragma once
#include "../include/Flow.h"
#include "../Foundation/FlowHelper.h"
#include "../Foundation/CAudioObject.h"
#include "../Foundation/CAudioObjectCreator.h"

// BEGIN: AUTO GEN DECLARE ENUM CODE
// declare enum type if need it
// END: AUTO GEN DECLARE ENUM CODE

typedef struct _CYourIP CYourIP;

struct _CYourIP
{
	CAudioObject* cao_base;
	
	// declare variable for audio processing
	int _channels;
	/* USER CODE BEGIN VarDeclare */
	
	/* USER CODE END VarDeclare */	

	// BEGIN: AUTO GEN DECLARE PARAM CODE
	// declare parameter CParam which display on Audio Object content
	// example, CParam* _pParam1;
	// END: AUTO GEN DECLARE PARAM CODE

};

FLOW_API extern CYourIP* CYourIP_New(void* addr, const char* instanceName, int numInChannels, int numOutChannels);
FLOW_API extern void CYourIP_Delete(CYourIP*);

/* Creator functinos for DspManager to dynamic create YourIP object*/
FLOW_API extern CAudioObject* YourIPCreator_CreateAudioObject(const char* instanceName, unsigned int numInChannels, unsigned int numOutChannels, struct hashmap_s paramList);
FLOW_API extern void YourIPCreator_parseParam(CAudioObject* obj, struct hashmap_s paramList);
