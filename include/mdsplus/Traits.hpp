#ifndef TRAITS_HPP
#define TRAITS_HPP

////////////////////////////////////////////////////////////////////////////////
//  ENABLE IF  /////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////

namespace MDSplus {

template <bool B, class T = void>
struct enable_if {
    typedef T type;
};

template <class T>
struct enable_if<false, T> {};

} // MDSplus


#endif // TRAITS_HPP

