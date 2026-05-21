#pragma once

#ifdef _WIN32
  #ifndef BUILD_STATIC
    #if defined(ARRAYMAKER_LIB)
      #define ARRAYMAKER_EXPORT __declspec(dllexport)
    #else
      #define ARRAYMAKER_EXPORT __declspec(dllimport)
    #endif
  #else
    #define ARRAYMAKER_EXPORT
  #endif
#else
  #ifndef BUILD_STATIC
    #if defined(ARRAYMAKER_LIB)
      #define ARRAYMAKER_EXPORT __attribute__((visibility("default")))
    #else
      #define ARRAYMAKER_EXPORT
    #endif
  #else
   #define ARRAYMAKER_EXPORT
  #endif
#endif
