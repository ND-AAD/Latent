// cpp_core/c_bindings/exports.h
#ifndef LATENT_EXPORTS_H
#define LATENT_EXPORTS_H

#ifdef _WIN32
    #ifdef LATENT_EXPORTS
        #define LATENT_API __declspec(dllexport)
    #else
        #define LATENT_API __declspec(dllimport)
    #endif
#else
    #define LATENT_API __attribute__((visibility("default")))
#endif

#endif // LATENT_EXPORTS_H
