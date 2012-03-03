%define major 4
%define libname %mklibname miredo %{major}
%define develname %mklibname miredo -d

Name:           miredo
Version:        1.2.5
Release:        1
Summary:        Tunneling of IPv6 over UDP through NATs

Group:          Networking/Other 
License:        GPLv2+
URL:            http://www.simphalempin.com/dev/miredo/
Source0:        http://www.remlab.net/files/miredo/miredo-%{version}.tar.xz
Source1:        miredo-client.init
Source2:        miredo-server.init
Patch0:         miredo-config-not-exec
Patch1:         reread-resolv-before-resolv-ipv4.patch

BuildRequires:    libcap-devel 

Requires(pre):    shadow-utils
Requires(post):   chkconfig, /sbin/ldconfig
# This is for /sbin/service
Requires(preun):  chkconfig, initscripts
Requires(postun): initscripts, /sbin/ldconfig

%description
Miredo is an implementation of the "Teredo: Tunneling IPv6 over UDP
through NATs" proposed Internet standard (RFC4380). It can serve
either as a Teredo client, a stand-alone Teredo relay, or a Teredo
server, please install the miredo-server or miredo-client aproprietly.
It is meant to provide IPv6 connectivity to hosts behind NAT
devices, most of which do not support IPv6, and not even
IPv6-over-IPv4 (including 6to4).

%package -n	%{libname}
Summary:        Tunneling of IPv6 over UDP through NATs
Group:          Networking/Other 

%description -n	%{libname}
Miredo is an implementation of the "Teredo: Tunneling IPv6 over UDP
through NATs" proposed Internet standard (RFC4380). It can serve
either as a Teredo client, a stand-alone Teredo relay, or a Teredo
server, please install the miredo-server or miredo-client aproprietly.
It is meant to provide IPv6 connectivity to hosts behind NAT
devices, most of which do not support IPv6, and not even
IPv6-over-IPv4 (including 6to4).
This libs package provides the files necessary for both server and client.


%package -n	%{develname}
Summary:        Header files, libraries and development documentation for %{name}
Group:          Networking/Other 
Requires:       %{libname} = %{version}-%{release}

%description -n	%{develname}
This package contains the header files, development libraries and development
documentation for %{name}. If you would like to develop programs using %{name},
you will need to install %{name}-devel.

%package server
Summary:        Tunneling server for IPv6 over UDP through NATs
Group:          Networking/Other 
Requires:       %{libname} = %{version}-%{release}
%description server
Miredo is an implementation of the "Teredo: Tunneling IPv6 over UDP
through NATs" proposed Internet standard (RFC4380). This offers the server 
part of miredo. Most people will need only the client part.

%package client
Summary:        Tunneling client for IPv6 over UDP through NATs
Group:          Networking/Other 
Requires:       %{libname} = %{version}-%{release}
Provides:       %{name} = %{version}-%{release}
Obsoletes:      %{name} <= 1.1.6


%description client
Miredo is an implementation of the "Teredo: Tunneling IPv6 over UDP
through NATs" proposed Internet standard (RFC4380). This offers the client
part of miredo. Most people only need the client part.

%prep
%setup -q
%patch0 -p1 
%patch1 -p1

%build
%configure \
               --disable-static \
               --disable-rpath \
               --enable-miredo-user \

# rpath does not really work
sed -i 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|g' libtool
sed -i 's|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|g' libtool
%make


%install

%makeinstall_std
%find_lang %{name}
mkdir rpmdocs
mv %{buildroot}%{_docdir}/miredo/examples rpmdocs/
mkdir -p %{buildroot}%{_initrddir}
install -p -m 755 %{SOURCE1} %{buildroot}%{_initrddir}/miredo-client
install -p -m 755 %{SOURCE2} %{buildroot}%{_initrddir}/miredo-server
rm -f %{buildroot}%{_libdir}/lib*.la
touch %{buildroot}%{_sysconfdir}/miredo/miredo-server.conf
mkdir -p %{buildroot}/lib/systemd/systemd/
cp %{buildroot}/%{_libdir}/systemd/system/%{name}.service %{buildroot}/lib/systemd/systemd/%{name}.service

rm -f %{buildroot}/%{_libdir}/systemd/system/%{name}.service


%pre -n %{libname}
getent group miredo >/dev/null || groupadd -r miredo
getent passwd miredo >/dev/null || useradd -r -g miredo -d /etc/miredo \
         -s /sbin/nologin -c "Miredo Daemon" miredo
exit 0

%post client 
/sbin/chkconfig --add miredo-client

%post server
/sbin/chkconfig --add miredo-server


%preun client
if [ $1 = 0 ] ; then
    /sbin/service miredo-client stop >/dev/null 2>&1
    /sbin/chkconfig --del miredo-client
fi

%preun server
if [ $1 = 0 ] ; then
    /sbin/service miredo-server stop >/dev/null 2>&1
    /sbin/chkconfig --del miredo-server
fi


%postun client
if [ "$1" -ge "1" ] ; then
    /sbin/service miredo-client condrestart >/dev/null 2>&1 || :
fi


%postun server
if [ "$1" -ge "1" ] ; then
    /sbin/service miredo-server condrestart >/dev/null 2>&1 || :
fi

%files -n %{libname} -f %{name}.lang
#% doc % {_mandir}/man?/miredo*
%dir %{_sysconfdir}/miredo
%{_libdir}/libteredo.so.*
%{_libdir}/libtun6.so.*
%{_libdir}/miredo/

%files -n %{develname}
%{_includedir}/libteredo/
%{_includedir}/libtun6/
%{_libdir}/libteredo.so
%{_libdir}/libtun6.so

%files server
%ghost %config(noreplace,missingok) %{_sysconfdir}/miredo/miredo-server.conf
%{_bindir}/teredo-mire
%{_sbindir}/miredo-server
%{_sbindir}/miredo-checkconf
%{_initrddir}/miredo-server
/lib/systemd/systemd/miredo.service
%doc %{_mandir}/man1/teredo-mire*
%doc %{_mandir}/man?/miredo-server*
%doc %{_mandir}/man?/miredo-checkconf*


%files client
%config(noreplace) %{_sysconfdir}/miredo/miredo.conf
%config(noreplace) %{_sysconfdir}/miredo/client-hook
%{_initrddir}/miredo-client
%{_sbindir}/miredo
%doc %{_mandir}/man?/miredo.*
