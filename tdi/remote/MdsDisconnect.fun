fun public MdsDisconnect(optional in _host, optional in _all)
{
  if (!Present(_all)) _all = 0; else _all = 1;
  if (!Present(_host))
    return ( MdsRemote->MdsDisconnect(Val(_all), Val(0)) );
  else
    return ( MdsRemote->MdsDisconnect(Val(_all), Ref(_host)) );
}
