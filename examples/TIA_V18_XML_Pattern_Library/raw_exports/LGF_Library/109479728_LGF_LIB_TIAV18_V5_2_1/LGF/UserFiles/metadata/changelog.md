# Change log

## [V5.2.1] - 10/2025

**UPDATED**

* LGF_DTLToString_DE / V3.1.1
  * Spelling errors

* LGF_DTLToString_ISO / V3.1.1
  * Spelling errors

* LGF_DTLToString_US / V1.0.1
  * Spelling errors

* LGF_MeasureCpuLoad / V1.1.1
  * Bugfixed error in loop

## [V5.2.0] - 08/2025

**GLOBAL** / V5.2.0

* Reduce number of templates, all others can be derived from the present templates

**NEW**

* LGF_ActDeactDevice / V2.0.0
  * First released version in different project
  * Refactoring & Improve Code for LGF Integration
  * Thats why we start here with V2.0 for the LGF integration
  * Copy of `LGF_ActDeactMonitorDevice` without device monitoring, just executing activation and deactivation

* LGF_ActDeactMonitorDevice / V2.0.0
  * First released version in different project
  * Refactoring & Improve Code for LGF Integration
  * Thats why we start here with V2.0 for the LGF integration

* LGF_ClockGen / V1.0.1
  * First released version
  * Integration into LGF

* LGF_DelayProgram / V1.0.0
  * First Release

* LGF_DTLToString_US / V1.0.0
  * First released version

* LGF_FileDelete / V1.0.0
  * First released version

* LGF_FileReadWriteDelete / V1.0.0
  * First released version

* LGF_GetClockState / V1.0.0
  * First released version

* LGF_IsNumber / V1.0.0
  * First release version

* LGF_MeasureCpuLoad / V1.1.0
  * First Release
  * Add Output with overall runtime incl. interrupts

* LGF_RoundByPrecision / V1.0.0
  * First released version

* LGF_SimpleAveraging / V1.0.0
  * First Release

* LGF_StartValueReadWrite / V1.0.0
  * First released version

* LGF_StringToDTL_US / V1.0.0
  * First released version

**UPDATED**

* LGF_Boxplot_DInt / V3.0.3
  * Fixed bug for array starting index
  * Fixed comments and block info header

* LGF_Boxplot_LReal / V3.0.3
  * Fixed bug for array starting index
  * Fixed comments and block info header

* LGF_Boxplot_UDInt / V3.0.3
  * Fixed bug for array starting index
  * Fixed comments and block info header

* LGF_DTLToString_DE / V3.1.0
  * Insert parameter for separator between Data and time
  * Assign default value '-' for separator parameter

* LGF_DTLToString_ISO / V3.1.0
  * Insert parameter for separator between Data and time
  * Assign default value '-' for separator parameter

* LGF_FIFO / V4.0.0
  * Rework to PLC Open `Enable` behavior
  * Add `isFull` outputs
  * Fix Bug while filling after left shift operation
  * Rework to diagnostic output datatype

* LGF_FileRead / V1.0.1
  * Add missing text in constant area

* LGF_FileWrite / V1.1.0
  * Insert parameter `clearBufferBefore` to clear buffer befor serializing the data

* LGF_Histogram_DInt / V3.0.3
  * Fixed bug for histValues Array
  * Fixed comments and block info header

* LGF_Histogram_LReal / V3.0.3
  * Fixed bug for histValues Array
  * Fixed comments and block info header

* LGF_Histogram_UDInt / V3.0.3
  * Fixed bug for histValues Array
  * Fixed comments and block info header

* LGF_Integration / V3.1.0
  * Fix bug - Time measurement and calculation for nanoseconds fixed
  * Fix Wording/Bug - Time measurement scaling [ms] / [s] - timing for calculatiuon is bnased on seconds

* LGF_LIFO / V4.0.0
  * Rework to PLC Open `Enable` behavior
  * Add `isFull` outputs
  * Rework to diagnostic output datatype

* LGF_MatrixScalarMultiplication / V3.0.2
  * Fix bug regarding wrong calculation

* LGF_ShiftRegister / V4.0.0
  * Rework to PLC Open `Enable` behavior
  * Add `reset` input / counter outputs
  * Fix Bug while filling after left shift operation
  * Rework to diagnostic output datatype

* LGF_StringToDTL_DE / V3.1.0
  * Fix bug - missing error code in case of wrong date string

* LGF_StringToDTL_ISO / V3.1.0
  * Fix bug - missing error code in case of wrong date string

* LGF_StringToTime / V3.1.0
  * Implemented separator functionality

* LGF_SwapBlockDWord / V1.0.2
  * Fixed comments and block info header
  * Fixed bug in loop upper index

* LGF_SwapBlockLWord / V1.0.2
  * Fixed comments and block info header
  * Fixed bug in loop upper index

* LGF_SwapBlockWord / V1.0.2
  * Fixed comments AND block info header
  * Fixed bug in loop upper index

* LGF_TimeToString / V3.1.0
  * Implemented separator input and functionality

## [V5.1.1] - 01/2024

**NEW**

* LGF_CompareString / V1.0.0
  * First released version

* LGF_CountArrayElements / V1.0.0
  * First released version

* LGF_DataLogC / V1.0.0
  * First released version

* LGF_DecodeUtf8 / V1.0.0
  * First released version

* LGF_DTLToJulianDate / V1.0.0
  * First released version

* LGF_EncodeUtf8 / V1.0.0
  * First released version

* LGF_ExtractStringFromCharArray / V1.1.0
  * First released version (LHttp)
  * Adaption and integration into LGF

* LGF_ExtractStringFromCharArrayAdv / V1.1.0
  * First released version (LHttp)
  * Adaption and integration into LGF

* LGF_FileRead / V1.0.0
  * First released version

* LGF_FileWrite / V1.0.0
  * First released version

* LGF_FindStringInCharArray / V1.1.0
  * First released version (LHttp)
  * Adaption and integration into LGF

* LGF_IecTimerOnOff / V1.0.0
  * First released version

* LGF_IsBigEndian / V1.0.0
  * First released version

* LGF_IsLittleEndian / V1.0.0
  * First released version

* LGF_IsValueInToleranceByTime / V1.0.0
  * First released version
  * Copied snd extended from "IsValueInRange"

* LGF_JulianTimeToDTL / V1.0.0
  * First released version

* LGF_ReadPnInterfaceParameter / V1.0.0
  * First released version

* LGF_SwapBlockDWord / V1.0.0
  * First released version

* LGF_SwapBlockLWord / V1.0.0
  * First released version

* LGF_SwapBlockWord / V1.0.0
  * First released version

* LGF_ToLower / V1.0.0
  * First released version

* LGF_ToUpper / V1.0.0
  * First released version

**RENAMED**

* LGF_DTLToString_DE / V3.0.1
  * Insert documentation

* LGF_DTLToString_ISO / V3.0.1
  * Insert documentation

* LGF_RandomRange_DInt / V3.0.1
  * Insert documentation

**UPDATED**

* LGF_CalcCRC16 / V3.1.0
  * Add input `noOfElements` to assign length to be converted different from array size
  * Add outputs `error` and `status` display a wrong assignment to `noOfElements`

* LGF_CalcCRC16Advanced / V3.1.0
  * Add input `noOfElements` to assign length to be converted different from array size
  * Add outputs `error` and `status` display a wrong assignment to `noOfElements`

* LGF_CalcCRC32 / V3.1.0
  * Add input `noOfElements` to assign length to be converted different from array size
  * Add outputs `error` and `status` display a wrong assignment to `noOfElements`

* LGF_CalcCRC32Advanced / V3.1.0
  * Add input `noOfElements` to assign length to be converted different from array size
  * Add outputs `error` and `status` display a wrong assignment to `noOfElements`

* LGF_CalcCRC8 / V3.1.0
  * Add input `noOfElements` to assign length to be converted different from array size
  * Add outputs `error` and `status` display a wrong assignment to `noOfElements`

* LGF_CalcCRC8Advanced / V3.1.0
  * Add input `noOfElements` to assign length to be converted different from array size
  * Add outputs `error` and `status` display a wrong assignment to `noOfElements`

* LGF_CompareLReal / V3.0.2
  * Fix compare error if one value is exactly zero

* LGF_CompareLRealByPrecision / V3.0.2
  * Fix compare error if one value is exactly zero

* LGF_CosinusCI / V3.0.2
  * Fix callculation of 'phaseShift'

* LGF_DTLToUnixTime / V3.0.2
  * Improve data verification for input `timeDTL` for valid data

* LGF_SearchMinMax_DInt / V3.0.2
  * Fix loop start index (start from lower Bound + 1)

* LGF_SearchMinMax_LReal / V3.0.2
  * Fix loop start index (start from lower Bound + 1)

* LGF_SetTime / V3.0.3
  * Bug fix - bias correction for time offsets (200)

* LGF_SinusCI / V3.0.2
  * Fix callculation of 'phaseShift'

* LGF_TimerSwitch / V3.1.0
  * Insert mode `permanently On`: `10`, `permanently Off`: `0`

## [V5.1.0] - 11/2021

**NEW**

* LGF_BinaryMaskCompare / V1.0.0
  * First released version

* LGF_CountBooleanEdges / V1.0.0
  * First released version

* LGF_GetBitStates / V1.0.0
  * First released version

* LGF_ShiftRegister / V3.0.0
  * First released version
  * Refactoring and alignment to Datatype Variant
  * Insert documentation

**UPDATED**

* LGF_AstroClock / V3.0.1
  * Bug fix - not enabled - block still running
  * Insert documentation

* LGF_AverageAndDeviation / V3.0.1
  * Insert documentation

* LGF_BinaryToGray / V3.0.1
  * Insert documentation

* LGF_BitCount / V3.0.2
  * Insert documentation

* LGF_BitReset / V3.0.1
  * Insert documentation

* LGF_BitSet / V3.0.1
  * Insert documentation

* LGF_BitSetTo / V3.0.1
  * Insert documentation

* LGF_BitTest / V3.0.1
  * Insert documentation

* LGF_BitToggle / V3.0.1
  * Insert documentation

* LGF_Boxplot_DInt / V3.0.1
  * Insert documentation

* LGF_Boxplot_LReal / V3.0.1
  * Insert documentation

* LGF_Boxplot_UDInt / V3.0.1
  * Insert documentation

* LGF_CalcCRC16 / V3.0.1
  * Insert documentation
  * Assign default start values to optional inputs - `initValue`, `mask`

* LGF_CalcCRC16Advanced / V3.0.1
  * Insert documentation
  * Assign default start values to optional inputs - `initValue`, `mask`, `finalXorValue`, `reflectInput`, `reflectResult`

* LGF_CalcCRC32 / V3.0.1
  * Insert documentation
  * Assign default start values to optional inputs - `initValue`, `mask`

* LGF_CalcCRC32Advanced / V3.0.1
  * Insert documentation
  * Assign default start values to optional inputs - `initValue`, `mask`, `finalXorValue`, `reflectInput`, `reflectResult`

* LGF_CalcCRC8 / V3.0.1
  * Insert documentation
  * Assign default start values to optional inputs - `initValue`, `mask`

* LGF_CalcCRC8Advanced / V3.0.1
  * Insert documentation
  * Assign default start values to optional inputs - `initValue`, `mask`, `finalXorValue`, `reflectInput`, `reflectResult`

* LGF_CalcCRC8For1Byte / V3.0.1
  * Insert documentation
  * Assign default start values to optional inputs - `initValue`, `mask`

* LGF_CalcDistance_2D / V3.0.1
  * Insert documentation

* LGF_CalcDistance_3D / V3.0.1
  * Insert documentation

* LGF_CelsiusToFahrenheit / V3.0.1
  * Insert documentation

* LGF_CelsiusToKelvin / V3.0.1
  * Insert documentation

* LGF_CompareLReal / V3.0.1
  * Insert documentation

* LGF_CompareLRealByPrecision / V3.0.1
  * Insert documentation

* LGF_CompareVariant / V3.0.1
  * Insert documentation

* LGF_ConvertTemperature / V3.0.1
  * Rename from "LGF_TemperatureConvert" to "LGF_ConvertTemperature"
  * to start with the verb
  * include the Rankine conversion
  * Code refactoring, regions, commends and constants
  * Set version to V3.0.0
  * harmonize the version of the whole library
  * Insert documentation

* LGF_CosinusCI / V3.0.1
  * Insert documentation

* LGF_CountFalInDWord / V3.0.1
  * Insert documentation

* LGF_CountRisInDWord / V3.0.1
  * Insert documentation

* LGF_DifferenceQuotientFB / V3.0.1
  * Insert documentation

* LGF_DifferenceQuotientFC / V3.0.1
  * Insert documentation

* LGF_DTLToString_DE / V3.0.1
  * Insert documentation

* LGF_DTLToString_ISO / V3.0.1
  * Insert documentation

* LGF_DTLToUnixTime / V3.0.1
  * Insert documentation

* LGF_FahrenheitToCelsius / V3.0.1
  * Insert documentation

* LGF_FahrenheitToKelvin / V3.0.1
  * Insert documentation

* LGF_FIFO / V3.0.1
  * Insert documentation

* LGF_FloatingAverage / V3.0.2
  * Insert documentation

* LGF_Frequency / V3.0.1
  * Insert documentation

* LGF_GetCalendarDay / V3.0.1
  * Insert documentation

* LGF_GetCalendarWeek_ISO / V3.0.1
  * Insert documentation

* LGF_GetCalendarWeek_US / V3.0.1
  * Insert documentation

* LGF_GetFactorial / V3.0.1
  * Insert documentation

* LGF_GpsDDToGps / V3.0.2
  * Fix `tempStatus` initialization
  * Insert documentation

* LGF_GpsToGpsDD / V3.0.2
  * Fix `tempStatus` initialization
  * Insert documentation

* LGF_GrayToBinary / V3.0.1
  * Insert documentation

* LGF_Histogram_DInt / V3.0.1
  * Insert documentation

* LGF_Histogram_LReal / V3.0.1
  * Insert documentation

* LGF_Histogram_UDInt / V3.0.1
  * Insert documentation

* LGF_Impulse / V3.0.1
  * Insert documentation

* LGF_Integration / V3.0.2
  * Insert documentation
  * Fix bug - incompatibility with S7-1200 and LTIME

* LGF_IntToString / V3.0.1
  * Insert documentation

* LGF_IsGermanHoliday / V3.0.1
  * fix bug in Constant "DAYS_AFTER_EASTER_60" from 6 to 60
  * Insert documentation

* LGF_IsParityEven / V3.0.1
  * Insert documentation

* LGF_IsParityOdd / V3.0.1
  * Insert documentation

* LGF_IsValueInLimits / V3.0.1
  * Insert documentation

* LGF_IsValueInRange / V3.0.1
  * Insert documentation

* LGF_IsValueInTolerance / V3.0.2
  * Bug fix - negative setpoint verification
  * Insert documentation

* LGF_KelvinToCelsius / V3.0.1
  * Insert documentation

* LGF_KelvinToFahrenheit / V3.0.1
  * Insert documentation

* LGF_KelvinToRankine / V3.0.1
  * Insert documentation

* LGF_LIFO / V3.0.1
  * Insert documentation

* LGF_LimRateOfChangeAdvancedCI / V3.0.1
  * Insert documentation

* LGF_LimRateOfChangeCI / V3.0.1
  * Insert documentation

* LGF_MatrixAddition / V3.0.1
  * Insert documentation

* LGF_MatrixCompare / V3.0.1
  * Insert documentation

* LGF_MatrixInverse / V3.0.1
  * Insert documentation

* LGF_MatrixMultiplication / V3.0.1
  * Insert documentation

* LGF_MatrixScalarMultiplication / V3.0.1
  * Insert documentation

* LGF_MatrixSubtraction / V3.0.1
  * Insert documentation

* LGF_MatrixTranspose / V3.0.1
  * Insert documentation

* LGF_MergeBitsToDWord / V3.0.1
  * Insert documentation

* LGF_MergeBitsToWord / V3.0.1
  * Insert documentation

* LGF_MergeBytesToDWord / V3.0.1
  * Insert documentation

* LGF_MergeBytesToWord / V3.0.1
  * Insert documentation

* LGF_MergeWordsToDWord / V3.0.1
  * Insert documentation

* LGF_NonLinearInterpolation / V3.0.1
  * Insert documentation

* LGF_NthRoot / V3.0.1
  * Insert documentation

* LGF_PulseRelay / V3.0.1
  * Insert documentation

* LGF_RampCI / V3.0.1
  * Insert documentation
  * Change UDT member name from `outValue` to `outputValue`

* LGF_Random_DInt / V3.0.1
  * Insert documentation

* LGF_Random_Real / V3.0.1
  * Insert documentation

* LGF_Random_UDInt / V3.0.1
  * Insert documentation

* LGF_RandomRange_DInt / V3.0.1
  * Insert documentation

* LGF_RandomRange_Real / V3.0.1
  * Insert documentation

* LGF_RandomRange_UDInt / V3.0.1
  * Insert documentation

* LGF_RankineToKelvin / V3.0.1
  * Insert documentation

* LGF_RectangleCI / V3.0.1
  * Insert documentation

* LGF_RegressionLine / V3.0.1
  * Insert documentation

* LGF_SawTooth / V3.0.1
  * Insert documentation

* LGF_SawToothCI / V3.0.1
  * Insert documentation

* LGF_ScaleLinear / V3.0.1
  * Insert documentation
  * Move to folder "Math operations"

* LGF_SearchMinMax / V3.0.1
  * Rework constants and comments
  * Insert documentation

* LGF_SearchMinMax_DInt / V3.0.1
  * Insert documentation

* LGF_SearchMinMax_LReal / V3.0.1
  * Insert documentation

* LGF_SearchMinMax_UDInt / V3.0.1
  * Insert documentation

* LGF_SetTime / V3.0.2
  * Bug fix - bias correction for time offsets (200 / 330)
  * Insert documentation

* LGF_ShellSort_DInt / V3.0.1
  * Insert documentation

* LGF_ShellSort_LReal / V3.0.1
  * Insert documentation

* LGF_ShellSort_UDInt / V3.0.1
  * Insert documentation

* LGF_SimpleSmoothingFB / V3.0.1
  * Insert documentation

* LGF_SimpleSmoothingFC / V3.0.1
  * Insert documentation

* LGF_SinusCI / V3.0.1
  * Insert documentation

* LGF_SmoothByPolynomFB / V3.0.1
  * Insert documentation

* LGF_SmoothByPolynomFC / V3.0.1
  * Insert documentation

* LGF_SplitByteToBits / V3.0.1
  * Insert documentation

* LGF_SplitDWordToBits / V3.0.1
  * Insert documentation

* LGF_SplitDWordToBytes / V3.0.1
  * Insert documentation

* LGF_SplitDWordToWords / V3.0.1
  * Insert documentation

* LGF_SplitWordToBits / V3.0.1
  * Insert documentation

* LGF_SplitWordToBytes / V3.0.1
  * Insert documentation

* LGF_StoreMinMax / V3.0.1
  * Insert documentation

* LGF_StringToDTL_DE / V3.0.1
  * Insert documentation

* LGF_StringToDTL_ISO / V3.0.1
  * Insert documentation

* LGF_StringToInt / V3.0.1
  * Insert documentation
  * ENO handling done by STRG_VAL system function

* LGF_StringToTaddr / V3.0.1
  * Insert documentation

* LGF_StringToTime / V3.0.1
  * Insert documentation

* LGF_TaddrToString / V3.0.1
  * Insert documentation

* LGF_TimerSwitch / V3.0.1
  * Insert documentation

* LGF_TimeToString / V3.0.1
  * Insert documentation

* LGF_TriangleCI / V3.0.1
  * Insert documentation

* LGF_UnixTimeToDTL / V3.0.1
  * Insert documentation

## [V5.0.1] - 04/2020

**NEW**

* LGF_AstroClock / V3.0.0
  * First released version
  * T_ADD instruction is replaced with "+"
  * "offsetSunrise", "offsetSunset" is calculated in
  * "daytime"
  * Bug fix at "Adjust back TO UTC"
  * Add output actSystemTime and actLocalTime
  * Add comments
  * Bug fix at calculation sunrise and sunset
  * Upgrade: TIA V14 Update 1
  * Code optimization
  * Initialize #tempIntSunrise, #tempIntSunset,#tempDate1Jan 
  * Upgrade: TIA V15 Update 2
  * Upgrade: TIA V15.1
  * Rename from Astro to AstroClock
  * Update Type name to positionGps - "LGF_typeGPS_DD" - GPS position as decimal degree
  * Refactoring of interface
  * - one input type for GPS data
  * - refactored for better usability
  * - refactoring of whole block to "ENABLE" behaviour
  * Set version to V3.0.0, harmonize the version of the whole library

* LGF_AverageAndDeviation / V3.0.0
  * First released version
  * Bug fix at WRONG_TYPE:  #error := true
  * Upgrade: TIA Portal V14 Update 1
  * Upgrade: TIA V15 Update 2
  * Upgrade: TIA V15.1
  * Data type changed from Variant to Array[*] of LReal
  * Regions,commens and constants are added
  * Set version to V3.0.0, harmonize the version of the whole library

* LGF_BinaryToGray / V3.0.0
  * First released version
  * Name changed
  * Upgrade: TIA Portal V14 Update 1
  * Upgrade: TIA V15 Update 2
  * Upgrade: TIA V15.1
  * Standard header and block parameters update
  * add eno handling
  * Set version to V3.0.0
  * harmonize the version of the whole library

* LGF_BitCount / V3.0.0
  * first release
  * Set version to V3.0.0
  * harmonize the version of the whole library

* LGF_BitReset / V3.0.0
  * first release
  * Set version to V3.0.0
  * harmonize the version of the whole library

* LGF_BitSet / V3.0.0
  * first release
  * Set version to V3.0.0
  * harmonize the version of the whole library

* LGF_BitSetTo / V3.0.0
  * first release
  * Set version to V3.0.0
  * harmonize the version of the whole library

* LGF_BitTest / V3.0.0
  * first release
  * Set version to V3.0.0
  * harmonize the version of the whole library

* LGF_BitToggle / V3.0.0
  * first release
  * Set version to V3.0.0
  * harmonize the version of the whole library

* LGF_Boxplot_DInt / V3.0.0
  * First released version
  * Code reworked, regions,commens and constants are added
  * Set version to V3.0.0, harmonize the version of the whole library

* LGF_Boxplot_LReal / V3.0.0
  * First released version
  * Set version to V3.0.0, harmonize the version of the whole library

* LGF_Boxplot_UDInt / V3.0.0
  * First released version
  * Set version to V3.0.0, harmonize the version of the whole library

* LGF_CalcCRC16 / V3.0.0
  * First released version
  * Upgrade: TIA V15 Update 2
  * Upgrade: TIA V15.1
  * Code refactoring, comments added
  * Set version to V3.0.0, harmonize the version of the whole library

* LGF_CalcCRC16Advanced / V3.0.0
  * first release, copied from "LGF_CalcCRC32Advanced"
  * Set version to V3.0.0, harmonize the version of the whole library

* LGF_CalcCRC32 / V3.0.0
  * First released version
  * Upgrade: TIA V15 Update 2
  * Upgrade: TIA V15.1
  * Code refactoring, comments added
  * Set version to V3.0.0, harmonize the version of the whole library

* LGF_CalcCRC32Advanced / V3.0.0
  * First released version
  * Upgrade: TIA V15 Update 2
  * Upgrade: TIA V15.1
  * Code refactoring, comments added
  * Set version to V3.0.0, harmonize the version of the whole library

* LGF_CalcCRC8 / V3.0.0
  * First released version
  * Upgrade: TIA V15 Update 2
  * Upgrade: TIA V15.1
  * Code refactoring, comments added
  * Set version to V3.0.0, harmonize the version of the whole library

* LGF_CalcCRC8Advanced / V3.0.0
  * first release, copied from "LGF_CalcCRC32Advanced"
  * Set version to V3.0.0, harmonize the version of the whole library

* LGF_CalcCRC8For1Byte / V3.0.0
  * First released version
  * Upgrade: TIA V15 Update 2
  * Upgrade: TIA V15.1
  * Code refactoring, comments added
  * Set version to V3.0.0, harmonize the version of the whole library

* LGF_CalcDistance_2D / V3.0.0
  * First released version
  * Upgrade: TIA V15 Update 2
  * Upgrade: TIA V15.1
  * Data type changed to LREAL
  * renamed from "Distance" to "CalcDistance_2D"
  * Data type changed to LREAL
  * Set version to V3.0.0, harmonize the version of the whole library

* LGF_CalcDistance_3D / V3.0.0
  * First released version
  * derivated from "CalcDistance_2D" and extended to 3D
  * Set version to V3.0.0, harmonize the version of the whole library

* LGF_CelsiusToFahrenheit / V3.0.0
  * First release
  * Set version to V3.0.0
  * harmonize the version of the whole library

* LGF_CelsiusToKelvin / V3.0.0
  * First release
  * Set version to V3.0.0
  * harmonize the version of the whole library

* LGF_CompareLReal / V3.0.0
  * First released version
  * Upgrade: TIA V15 Update 2
  * Upgrade: TIA V15.1
  * Refactoring and performance improvment
  * Delete Error and Status there is no need for,
  * because of changed / adjusted algorithm
  * add eno handling
  * Set version to V3.0.0, harmonize the version of the whole library

* LGF_CompareLRealByPrecision / V3.0.0
  * First released version
  * function besad on "LGF_CompareLReal"
  * Set version to V3.0.0, harmonize the version of the whole library

* LGF_CompareVariant / V3.0.0
  * First released version
  * Bug fix
  * Upgrade: TIA V14 Update 1
  * Upgrade: TIA V15 Update 2
  * Upgrade: TIA V15.1
  * Refactoring and performance improvment
  * Change error handling to status and subFctStatus
  * update serialize instruction
  * add eno handling
  * Set version to V3.0.0, harmonize the version of the whole library

* LGF_ConvertTemperature / V16.12.2018
  * First released version
  * Upgrade: TIA Portal V14 Update 1
  * Upgrade: TIA V15 Update 2
  * Upgrade: TIA V15.1
  * Siemens Industry Support 
  * harmonize the version of the whole library

* LGF_CosinusCI / V3.0.0
  * First released version
  * Upgrade: TIA V15 Update 2
  * Upgrade: TIA V15.1
  * Code refactoring, comments added,
  * phase shift availabilty added
  * Set version to V3.0.0, harmonize the version of the whole library

* LGF_CountFalInDWord / V3.0.0
  * First released version
  * Code refactoring - minimize used code memory
  * Set version to V3.0.0, harmonize the version of the whole libraryENO not in use, no error handling needed

* LGF_CountRisInDWord / V3.0.0
  * First released version
  * Code refactoring - minimize used code memory
  * Set version to V3.0.0, harmonize the version of the whole library

* LGF_DifferenceQuotientFB / V3.0.0
  * First released version
  * Code reworked.
  * Regions,commens and constants are added
  * Set version to V3.0.0, harmonize the version of the whole library

* LGF_DifferenceQuotientFC / V3.0.0
  * First released version
  * Regions,commens and constants are added
  * Set version to V3.0.0, harmonize the version of the whole library

* LGF_DTLToString_DE / V3.0.0
  * First released version
  * split from "LGF_DTLToString"
  * Set version to V3.0.0
  * harmonize the version of the whole library

* LGF_DTLToString_ISO / V3.0.0
  * First released version
  * Upgrade: TIA Portal V14 Update 1
  * Upgrade: TIA V15 Update 2
  * Upgrade: TIA V15.1
  * BUgfix - nanosecond precision and '0' filling
  * renamed from "LGF_DTLToString" to "LGF_DTLToString_ISO"
  * split into two blocks, removed "format" input
  * Set version to V3.0.0
  * harmonize the version of the whole library

* LGF_DTLToUnixTime / V3.0.0
  * First released version
  * Standard header and block parameters update, status parameter added
  * commends added and code refactoring
  * add eno handling
  * Set version to V3.0.0
  * harmonize the version of the whole library

* LGF_FahrenheitToCelsius / V3.0.0
  * First release
  * Set version to V3.0.0
  * harmonize the version of the whole library

* LGF_FahrenheitToKelvin / V3.0.0
  * First release
  * Set version to V3.0.0
  * harmonize the version of the whole library

* LGF_FIFO / V3.0.0
  * First released version
  * Bug fix resetBuffer
  * Upgrade: TIA Portal V14 Update 1
  * Upgrade: TIA V15 Update 2
  * Upgrade: TIA V15.1
  * Output "done" removed (not necessary, because block works synchron)
  * Code refactoring, comments added
  * Interface change (enqueue, dequeue etc.)
  * Set version to V3.0.0, harmonize the version of the whole library

* LGF_FloatingAverage / V3.0.1
  * First released version
  * Upgrade: TIA Portal V14 Update 1
  * Adding variable window size for calculation
  * Optimizing calculation algorithm
  * Upgrade: TIA V15 Update 2
  * Upgrade: TIA V15.1
  * Code refactoring, comments added
  * Set version to V3.0.0, harmonize the version of the whole library
  * refactor and simplify code

* LGF_Frequency / V3.0.0
  * First released version
  * New function: pulse pause ratio
  * Add comments
  * Upgrade: TIA Portal V14 Update 1
  * Upgrade: TIA V15 Update 2
  * Upgrade: TIA V15.1
  * Code refactoring, regions and more commens added 
  * Set version to V3.0.0, harmonize the version of the whole library

* LGF_GetCalendarDay / V3.0.0
  * First release
  * ENO used for internal error handling, interface has error and status
  * temp tag naming, insert constant
  * Set version to V3.0.0, harmonize the version of the whole library

* LGF_GetCalendarWeek_ISO / V3.0.0
  * First released version
  * Upgrade: TIA V15 Update 2
  * Upgrade: TIA V15.1
  * renamed from LGF_CalenderWeek to LGF_CalenderWeek_ISO
  * Function splitted into week for ISO and US Format and as well day counter.
  * Result passed as return value.
  * Standard header implemented
  * Constant, temp variable naming
  * Update function call of CalendarDay
  * Set version to V3.0.0, harmonize the version of the whole library

* LGF_GetCalendarWeek_US / V3.0.0
  * First release
  * based on LGF_CalenderWeek (because of split)
  * Set version to V3.0.0, harmonize the version of the whole library

* LGF_GetFactorial / V3.0.0
  * First released version
  * Upgrade: TIA V15 Update 2
  * Upgrade: TIA V15.1
  * Renamed from "Factorial" to "GetFactorial"
  * Code refactoring, regions and more commens added
  * Reworked to case of, MAGIC numbers are okay as they stay for the number/case itself
  * Set version to V3.0.0, harmonize the version of the whole library

* LGF_GpsDDToGps / V3.0.0
  * First released version
  * Set version to V3.0.0
  * harmonize the version of the whole library

* LGF_GpsToGpsDD / V3.0.0
  * First released version
  * Set version to V3.0.0
  * harmonize the version of the whole library

* LGF_GrayToBinary / V3.0.0
  * First released version
  * Name changed
  * Upgrade: TIA Portal V14 Update 1
  * Upgrade: TIA V15 Update 2
  * Upgrade: TIA V15.1
  * Standard header,block parameters update and performance update
  * add eno handling
  * Set version to V3.0.0
  * harmonize the version of the whole library

* LGF_Histogram_DInt / V3.0.0
  * First released version
  * Code refactoring, comments added
  * Set version to V3.0.0, harmonize the version of the whole library

* LGF_Histogram_LReal / V3.0.0
  * First released version
  * Code refactoring, comments added
  * Set version to V3.0.0, harmonize the version of the whole library

* LGF_Histogram_UDInt / V3.0.0
  * First released version
  * Code refactoring, comments added
  * Set version to V3.0.0, harmonize the version of the whole library

* LGF_Impulse / V3.0.0
  * First released version
  * LGF_Impulse calls new LGF_Frequency V1.1.1
  * Upgrade: TIA Portal V14 Update 1
  * Code optimization: no call of LGF_Frequency
  * Fix at output "countdown"
  * Upgrade: TIA V15 Update 2
  * Upgrade: TIA V15.1
  * Code refactoring, regions and more commens added
  * Set version to V3.0.0, harmonize the version of the whole library                    

* LGF_Integration / V3.0.0
  * First released version
  * Upgrade: TIA V15 Update 2
  * Upgrade: TIA V15.1
  * Regions,commens and constants are added, code refactored
  * Set version to V3.0.0, harmonize the version of the whole library

* LGF_IntToString / V3.0.0
  * First released version
  * Upgrade: TIA V15 Update 2
  * Upgrade: TIA V15.1
  * Standard header and block parameters update
  * Program changed to VAL_STRG wrapper
  * add eno handling
  * Set version to V3.0.0
  * harmonize the version of the whole library

* LGF_IsGermanHoliday / V3.0.0
  * First released version
  * Upgrade: TIA V15 Update 2
  * Upgrade: TIA V15.1
  * Standard header, comments, style updated
  * refactoring code
  * Set version to V3.0.0, harmonize the version of the whole library

* LGF_IsParityEven / V3.0.0
  * First released version
  * Set version to V3.0.0
  * harmonize the version of the whole library

* LGF_IsParityOdd / V3.0.0
  * First released version
  * Set version to V3.0.0
  * harmonize the version of the whole library

* LGF_IsValueInLimits / V3.0.0
  * First released version
  * Copied from "IsValueInRange"
  * Set version to V3.0.0, harmonize the version of the whole library

* LGF_IsValueInRange / V3.0.0
  * First released version
  * Upgrade: TIA V15 Update 2
  * Upgrade: TIA V15.1
  * renamed from "LGF_HighLowLimit" to "LGF_IsValueInRange"
  * Code refacturing
  * error values changed,regions,commens and costants are added
  * Set version to V3.0.0, harmonize the version of the whole library

* LGF_IsValueInTolerance / V3.0.0
  * First released version
  * Copied from "IsValueInRange"
  * Set version to V3.0.0, harmonize the version of the whole library

* LGF_KelvinToCelsius / V3.0.0
  * First release
  * Set version to V3.0.0
  * harmonize the version of the whole library

* LGF_KelvinToFahrenheit / V3.0.0
  * First release
  * Set version to V3.0.0
  * harmonize the version of the whole library

* LGF_KelvinToRankine / V3.0.0
  * First release
  * Set version to V3.0.0
  * harmonize the version of the whole library

* LGF_LIFO / V3.0.0
  * First released version
  * Upgrade: TIA V15 Update 2
  * Upgrade: TIA V15.1
  * Output "done" removed (not necessary, because block works synchron)
  * Code refactoring, comments added
  * Interface change (push, pop, peek etc.)
  * Set version to V3.0.0, harmonize the version of the whole library

* LGF_LimRateOfChangeAdvancedCI / V3.0.0
  * First released version
  * Upgrade: TIA Portal V14 Update 1
  * Upgrade: TIA V15 Update 2
  * Upgrade: TIA V15.1
  * Regions,commens and costants are added
  * Set version to V3.0.0, harmonize the version of the whole library

* LGF_LimRateOfChangeCI / V3.0.0
  * First released version
  * Upgrade: TIA Portal V14 Update 1
  * Upgrade: TIA V15 Update 2
  * Upgrade: TIA V15.1
  * Regions,commens and costants are added
  * Set version to V3.0.0, harmonize the version of the whole library

* LGF_MatrixAddition / V3.0.0
  * First released version
  * Upgrade: TIA Portal V14 Update 1
  * Functionality using Array[*,*]
  * Upgrade: TIA V15 Update 2
  * Upgrade: TIA V15.1
  * Regions,commens and costants are added
  * Moved matrices to IO field.
  * Set version to V3.0.0, harmonize the version of the whole library

* LGF_MatrixCompare / V3.0.0
  * First release
  * Set version to V3.0.0, harmonize the version of the whole library

* LGF_MatrixInverse / V3.0.0
  * First released version
  * Upgrade: TIA Portal V14 Update 1
  * Functionality using Array[*,*]
  * Upgrade: TIA V15 Update 2
  * Upgrade: TIA V15.1
  * Regions, comments and constants are added
  * Moved matrices to IO field.
  * Set version to V3.0.0, harmonize the version of the whole library

* LGF_MatrixMultiplication / V3.0.0
  * First released version
  * Upgrade: TIA Portal V14 Update 1
  * Functionality using Array[*,*]
  * Upgrade: TIA V15 Update 2
  * Upgrade: TIA V15.1
  * Regions,commens and costants are added
  * Moved matrices to IO field.
  * Set version to V3.0.0, harmonize the version of the whole library

* LGF_MatrixScalarMultiplication / V3.0.0
  * First released version
  * based on "LGF_MatrixMultiplication"
  * Set version to V3.0.0, harmonize the version of the whole library

* LGF_MatrixSubtraction / V3.0.0
  * First released version
  * Upgrade: TIA Portal V14 Update 1
  * Functionality using Array[*,*]
  * Upgrade: TIA V15 Update 2
  * Regions,commens and costants are added
  * Moved matrices to IO field.
  * Set version to V3.0.0, harmonize the version of the whole library

* LGF_MatrixTranspose / V3.0.0
  * First released version
  * Upgrade: TIA Portal V14 Update 1
  * Functionality using Array[*,*]
  * Upgrade: TIA V15 Update 2
  * Upgrade: TIA V15.1
  * Regions, comments and constants are added
  * Moved matrices to IO field.
  * Set version to V3.0.0, harmonize the version of the whole library

* LGF_MergeBitsToByte / V3.0.1
  * First release
  * Set version to V3.0.0
  * harmonize the version of the whole library
  * Insert documentation

* LGF_MergeBitsToDWord / V3.0.0
  * First release
  * Set version to V3.0.0
  * harmonize the version of the whole library

* LGF_MergeBitsToWord / V3.0.0
  * First released version
  * Upgrade: TIA V15 Update 2
  * Upgrade: TIA V15.1
  * Standard header, style guide
  * add ENO handling
  * Set version to V3.0.0
  * harmonize the version of the whole library

* LGF_MergeBytesToDWord / V3.0.0
  * First release
  * Set version to V3.0.0
  * harmonize the version of the whole library

* LGF_MergeBytesToWord / V3.0.0
  * First release
  * Set version to V3.0.0
  * harmonize the version of the whole library

* LGF_MergeWordsToDWord / V3.0.0
  * First release
  * Set version to V3.0.0
  * harmonize the version of the whole library

* LGF_NonLinearInterpolation / V3.0.0
  * First released version
  * Upgrade: TIA V15 Update 2
  * Upgrade: TIA V15.1
  * Regions,commens and costants are added
  * Set version to V3.0.0, harmonize the version of the whole library

* LGF_NthRoot / V3.0.0
  * First released version
  * Upgrade: TIA Portal V14 Update 1
  * Upgrade: TIA V15 Update 2
  * Upgrade: TIA V15.1
  * Calculation changed
  * Renamed from "LGF_XRoot" to "LGF_NthRoot"
  * Regions,commens and costants are added
  * Set version to V3.0.0, harmonize the version of the whole library

* LGF_PulseRelay / V3.0.0
  * First released version
  * Upgrade: TIA V14 Update 1
  * Comment correction                  
  * Upgrade: TIA V15 Update 2
  * Upgrade: TIA V15.1
  * Refactoring and performance improvment
  * add eno handling
  * Set version to V3.0.0, harmonize the version of the whole library

* LGF_RampCI / V3.0.0
  * First released version
  * Comment correction (REGION)
  * Upgrade: TIA V15 Update 2
  * Upgrade: TIA V15.1
  * Code optimization.
  * Commens and costants are added
  * Set version to V3.0.0, harmonize the version of the whole library

* LGF_Random_DInt / V3.0.0
  * First release
  * copied from "LGF_Random_Real"
  * Set version to V3.0.0, harmonize the version of the whole library

* LGF_Random_Real / V3.0.0
  * First released version
  * Upgrade: TIA V15 Update 2
  * Upgrade: TIA V15.1
  * Renamed from "LGF_RandomBasic" to "LGF_Random_Real"
  * Regions, commens and costants are added
  * Set version to V3.0.0, harmonize the version of the whole library

* LGF_Random_UDInt / V3.0.0
  * First release
  * copied from "LGF_Random_Real"
  * Set version to V3.0.0, harmonize the version of the whole library

* LGF_RandomRange_DInt / V3.0.0
  * First released version
  * Upgrade: TIA Portal V14 Update 1
  * Upgrade: TIA V15 Update 2
  * Upgrade: TIA V15.1
  * Renamed from "LGF_RandomInt" to "LGF_RandomRange_DInt"
  * change random datatype from int to dint
  * Regions, commens and costants are added
  * Set version to V3.0.0, harmonize the version of the whole library

* LGF_RandomRange_Real / V3.0.0
  * First released version
  * Upgrade: TIA Portal V14 Update 1
  * Bugfix: FC number
  * Upgrade: TIA V15 Update 2
  * Upgrade: TIA V15.1
  * Renamed from "LGF_RandomReal" to "LGF_RandomRange_Real"
  * Regions, commens and costants are added
  * Set version to V3.0.0, harmonize the version of the whole library

* LGF_RandomRange_UDInt / V3.0.0
  * First released version
  * copied from "LGF_RandomRange_DInt"
  * Set version to V3.0.0, harmonize the version of the whole library

* LGF_RankineToKelvin / V3.0.0
  * First release
  * Set version to V3.0.0
  * harmonize the version of the whole library

* LGF_RectangleCI / V3.0.0
  * First released version
  * Upgrade: TIA V15 Update 2
  * Upgrade: TIA V15.1
  * Code refactoring, comments added,
  * phase shift availabilty added
  * Set version to V3.0.0, harmonize the version of the whole library

* LGF_RegressionLine / V3.0.0
  * First released version
  * Code refactoring, comments added
  * Set version to V3.0.0, harmonize the version of the whole library

* LGF_SawTooth / V1.0.10
  * First released version
  * Bug fix
  * Upgrade: TIA Portal V14 Update 1
  * Upgrade: TIA V15 Update 2
  * Upgrade: TIA V15.1
  * Code refactoring, regions and more commens added                     

* LGF_SawToothCI / V3.0.0
  * First released version
  * Upgrade: TIA V15 Update 2
  * Upgrade: TIA V15.1
  * Code refactoring, regions and more commens added,
  * phase shift availabilty added
  * Set version to V3.0.0, harmonize the version of the whole library

* LGF_ScaleLinear / V3.0.0
  * First released version
  * Upgrade: TIA V15 Update 2
  * Upgrade: TIA V15.1
  * Data type changed from Variant to LReal
  * Standard header and block parameters update, status parameter added
  * LReal value comparison added
  * Result paramter changed to return value of FC for use in SCL
  * Warning nummber changed to range of 16#6xxx
  * refactor variablehandling and extract returns inbetween the code
  * add eno handling
  * Set version to V3.0.0
  * harmonize the version of the whole library

* LGF_SearchMinMax / V3.0.0
  * First released version
  * Upgrade: TIA Portal V14 Update 1
  * Upgrade: TIA V15 Update 2
  * Upgrade: TIA V15.1
  * Code refactoring, regions and more commens added
  * Set version to V3.0.0, harmonize the version of the whole library

* LGF_SearchMinMax_DInt / V3.0.0
  * First release
  * copied from "LGF_SearchMinMax" and reworked to array[*]
  * Set version to V3.0.0, harmonize the version of the whole library

* LGF_SearchMinMax_LReal / V3.0.0
  * First release
  * copied from "LGF_SearchMinMax" and reworked to array[*]
  * Set version to V3.0.0, harmonize the version of the whole library

* LGF_SearchMinMax_UDInt / V3.0.0
  * First release
  * copied from "LGF_SearchMinMax" and reworked to array[*]
  * Set version to V3.0.0, harmonize the version of the whole library

* LGF_SetTime / V3.0.0
  * First released version
  * Upgrade: TIA V14 Update 1
  * Bugfix: FB number: automatic
  * Upgrade: TIA V15 Update 2
  * Upgrade: TIA V15.1
  * Bugfix: Rising edge at input REQ of SET_TIMEOUT
  * Reworked interface to PLC Open "execute" behaviour
  * Magic numbers removed, tag naming added, code reworked
  * Set version to V3.0.0, harmonize the version of the whole library

* LGF_ShellSort_DInt / V3.0.0
  * First released version
  * New function: reverse sort
  * Upgrade: TIA Portal V14 Update 1
  * Upgrade: TIA V15 Update 2
  * Upgrade: TIA V15.1
  * Output "done" removed (not necessary, because only one cycle)
  * Code refactoring, comments added,
  * change data type from Int to DInt
  * Set version to V3.0.0, harmonize the version of the whole library

* LGF_ShellSort_LReal / V3.0.0
  * First released version
  * New function: reverse sort
  * Upgrade: TIA Portal V14 Update 1
  * Upgrade: TIA V15 Update 2
  * Upgrade: TIA V15.1
  * Output "done" removed (not necessary, because only one cycle)
  * Code refactoring, comments added,
  * change data type from Real to LReal
  * Set version to V3.0.0, harmonize the version of the whole library

* LGF_ShellSort_UDInt / V3.0.0
  * First released version
  * New function: reverse sort
  * Upgrade: TIA Portal V14 Update 1
  * Upgrade: TIA V15 Update 2
  * Upgrade: TIA V15.1
  * Output "done" removed (not necessary, because only one cycle)
  * Code refactoring, comments added,
  * change data type from UInt to UDInt
  * Set version to V3.0.0, harmonize the version of the whole library

* LGF_SimpleSmoothingFB / V3.0.0
  * First released version
  * Regions,commens and constants are added  
  * Set version to V3.0.0, harmonize the version of the whole library

* LGF_SimpleSmoothingFC / V3.0.0
  * First released version
  * Regions,commens and constants are added
  * Set version to V3.0.0, harmonize the version of the whole library

* LGF_SinusCI / V3.0.0
  * First released version
  * Upgrade: TIA V15 Update 2
  * Upgrade: TIA V15.1
  * Code refactoring, comments added,
  * phase shift availabilty added
  * Set version to V3.0.0, harmonize the version of the whole library

* LGF_SmoothByPolynomFB / V3.0.0
  * First released version
  * BugFixes,Regions,commens and constants are added
  * Set version to V3.0.0, harmonize the version of the whole library

* LGF_SmoothByPolynomFC / V3.0.0
  * First released version
  * Regions,commens and constants are added
  * Set version to V3.0.0, harmonize the version of the whole library

* LGF_SplitByteToBits / V3.0.0
  * First release
  * Set version to V3.0.0
  * harmonize the version of the whole library

* LGF_SplitDWordToBits / V3.0.0
  * First release
  * Set version to V3.0.0
  * harmonize the version of the whole library

* LGF_SplitDWordToBytes / V3.0.0
  * First release
  * Set version to V3.0.0
  * harmonize the version of the whole library

* LGF_SplitDWordToWords / V3.0.0
  * First release
  * Set version to V3.0.0
  * harmonize the version of the whole library

* LGF_SplitWordToBits / V3.0.0
  * First released version
  * Upgrade: TIA V15 Update 2
  * Upgrade: TIA V15.1
  * Standard header, style guide
  * add ENO handling
  * Set version to V3.0.0
  * harmonize the version of the whole library

* LGF_SplitWordToBytes / V3.0.0
  * First release
  * Set version to V3.0.0
  * harmonize the version of the whole library

* LGF_StoreMinMax / V3.0.0
  * First released version
  * Upgrade: TIA Portal V14 Update 1
  * Code optimization
  * Upgrade: TIA V15 Update 2
  * Upgrade: TIA V15.1
  * Regions,commens and costants are added
  * Set version to V3.0.0, harmonize the version of the whole library

* LGF_StringToDTL_DE / V3.0.0
  * First released version
  * Split from "LGF_StringToDTL"
  * Correction of the weekday of DTL, comments added
  * add ENO handling, adjust comments in interface
  * Set version to V3.0.0
  * harmonize the version of the whole library

* LGF_StringToDTL_ISO / V3.0.0
  * First released version
  * Upgrade: TIA Portal V14 Update 1
  * Upgrade: TIA V15 Update 2
  * Upgrade: TIA V15.1
  * Reworked from "LGF_StringToDTL" to "LGF_StringToDTL_ISO"
  * removed format and split into two blocks
  * Bugfix - set weekday correctly
  * Correction of the weekday of DTL, comments added
  * add ENO handling, adjust comments in interface
  * Set version to V3.0.0
  * harmonize the version of the whole library

* LGF_StringToInt / V3.0.0
  * First released version
  * add eno handling
  * Set version to V3.0.0
  * harmonize the version of the whole library

* LGF_StringToTaddr / V3.0.0
  * First released version
  * Upgrade: TIA V15 Update 2
  * Upgrade: TIA V15.1
  * Standard header and block parameters update
  * Code refactoring and performance improvments
  * add eno handling
  * Set version to V3.0.0
  * harmonize the version of the whole library

* LGF_StringToTime / V3.0.0
  * First released version
  * Further improvments and codeoptimization 
  * add eno handling
  * Set version to V3.0.0
  * harmonize the version of the whole library

* LGF_TaddrToString / V3.0.0
  * First released version
  * Upgrade: TIA V15 Update 2
  * Upgrade: TIA V15.1
  * Standard header and block parameters update
  * refactoring of While to Do/While and constants inserted
  * add eno handling
  * Set version to V3.0.0
  * harmonize the version of the whole library

* LGF_TimerSwitch / V3.0.0
  * First released version
  * Fix in mode 2
  * New mode 5 + 6
  * New output: actLocalTime
  * Upgrade: TIA V14 Update 1
  * Fix in modes 1, 3, 5, 6                    
  * Upgrade: TIA V15 Update 2
  * Connection to type restored
  * Upgrade: TIA V15.1
  * Magic numbers removed, tag naming added, code reworked
  * Set version to V3.0.0, harmonize the version of the whole library

* LGF_TimeToString / V3.0.0
  * First released version
  * Upgrade: TIA V15 Update 2
  * Upgrade: TIA V15.1
  * Standard header and block parameters update, status parameter added
  * further improvments minimization and commends added
  * add eno handling
  * Set version to V3.0.0
  * harmonize the version of the whole library

* LGF_TriangleCI / V3.0.0
  * First released version
  * Upgrade: TIA V15 Update 2
  * Upgrade: TIA V15.1
  * Code refactoring, comments added,
  * phase shift availabilty added
  * Set version to V3.0.0, harmonize the version of the whole library

* LGF_UnixTimeToDTL / V3.0.0
  * First released version
  * Standard header and block parameters update, status parameter added
  * commends added and code intention addjusted
  * add eno handling
  * Set version to V3.0.0
  * harmonize the version of the whole library
