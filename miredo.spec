%define major_teredo 5
%define major_tun6 0
%define libteredo %mklibname teredo %{major_teredo}
%define libtun6 %mklibname tun 6 %{major_tun6}
%define devname %mklibname miredo -d

Summary:	Tunneling of IPv6 over UDP through NATs
Name:		miredo
Version:	1.2.6
Release:	1
License:	GPLv2+
Group:		Networking/Other
Url:		http://www.simphalempin.com/dev/miredo/
Source0:	http://www.remlab.net/files/miredo/miredo-%{version}.tar.xz
Source1:	miredo-client.service
Source2:	miredo-server.service
Patch0:		miredo-config-not-exec
Patch1:		reread-resolv-before-resolv-ipv4.patch
Patch2:		miredo-1.2.6-systemd.patch
BuildRequires:	gettext-devel
BuildRequires:	libcap-devel

Requires(pre):	shadow-utils
Requires(post,preun):	rpm-helper
Requires(preun,postun):	initscripts

%description
Miredo is an implementation of the "Teredo: Tunneling IPv6 over UDP
through NATs" proposed Internet standard (RFC4380). It can serve
either as a Teredo client, a stand-alone Teredo relay, or a Teredo
server. Please install the miredo-server or miredo-client appropriately.
It is meant to provide IPv6 connectivity to hosts behind NAT
devices, most of which do not support IPv6, and not even
IPv6-over-IPv4 (including 6to4).

#----------------------------------------------------------------------------

%package -n %{libteredo}
Summary:	Tunneling of IPv6 over UDP through NATs
Group:		Networking/Other
Conflicts:	%{_lib}miredo4 < 1.2.6
Obsoletes:	%{_lib}miredo4 < 1.2.6

%description -n %{libteredo}
Miredo is an implementation of the "Teredo: Tunneling IPv6 over UDP
through NATs" proposed Internet standard (RFC4380). It can serve
either as a Teredo client, a stand-alone Teredo relay, or a Teredo
server. Please install the miredo-server or miredo-client appropriately.
It is meant to provide IPv6 connectivity to hosts behind NAT
devices, most of which do not support IPv6, and not even
IPv6-over-IPv4 (including 6to4).

%files -n %{libteredo}
%{_libdir}/libteredo.so.%{major_teredo}*

#----------------------------------------------------------------------------

%package -n %{libtun6}
Summary:	Tunneling of IPv6 over UDP through NATs
Group:		Networking/Other
Conflicts:	%{_lib}miredo4 < 1.2.6

%description -n %{libtun6}
Miredo is an implementation of the "Teredo: Tunneling IPv6 over UDP
through NATs" proposed Internet standard (RFC4380). It can serve
either as a Teredo client, a stand-alone Teredo relay, or a Teredo
server. Please install the miredo-server or miredo-client appropriately.
It is meant to provide IPv6 connectivity to hosts behind NAT
devices, most of which do not support IPv6, and not even
IPv6-over-IPv4 (including 6to4).

%files -n %{libtun6}
%{_libdir}/libtun6.so.%{major_tun6}*

#----------------------------------------------------------------------------

%package -n %{devname}
Summary:	Header files, libraries and development documentation for %{name}
Group:		Networking/Other
Requires:	%{libteredo} = %{EVRD}
Requires:	%{libtun6} = %{EVRD}
Provides:	%{name}-devel = %{EVRD}

%description -n %{devname}
This package contains the header files, development libraries and development
documentation for %{name}. If you would like to develop programs using %{name},
you will need to install %{name}-devel.

%files -n %{devname}
%{_includedir}/libteredo/
%{_includedir}/libtun6/
%{_libdir}/libteredo.so
%{_libdir}/libtun6.so

#----------------------------------------------------------------------------

%package server
Summary:	Tunneling server for IPv6 over UDP through NATs
Group:		Networking/Other

%description server
Miredo is an implementation of the "Teredo: Tunneling IPv6 over UDP
through NATs" proposed Internet standard (RFC4380). This offers the server
part of miredo. Most people will need only the client part.

%files server
%ghost %config(noreplace,missingok) %{_sysconfdir}/miredo/miredo-server.conf
%{_bindir}/teredo-mire
%{_sbindir}/miredo-server
%{_sbindir}/miredo-checkconf
%{_unitdir}/miredo-server.service
%doc %{_mandir}/man1/teredo-mire*
%doc %{_mandir}/man?/miredo-server*
%doc %{_mandir}/man?/miredo-checkconf*

%preun server
%_preun_service server

#----------------------------------------------------------------------------

%package client
Summary:	Tunneling client for IPv6 over UDP through NATs
Group:		Networking/Other
Provides:	%{name} = %{EVRD}

%description client
Miredo is an implementation of the "Teredo: Tunneling IPv6 over UDP
through NATs" proposed Internet standard (RFC4380). This offers the client
part of miredo. Most people only need the client part.

%files client
%{_sbindir}/miredo
%doc %{_mandir}/man?/miredo.*
%{_unitdir}/miredo-client.service

#----------------------------------------------------------------------------

%package common
Summary:	Tunneling client for IPv6 over UDP through NATs
Group:		Networking/Other
Requires:	%{name}-client = %{EVRD}
Requires:	%{name}-server = %{EVRD}
Conflicts:	%{_lib}miredo4 < 1.2.6

%description common
Miredo is an implementation of the "Teredo: Tunneling IPv6 over UDP
through NATs" proposed Internet standard (RFC4380). This offers the client
part of miredo. Most people only need the client part.
Common package, that contains miredo-client and miredo-server

%files common -f %{name}.lang
%{_unitdir}/miredo.service
%{_libexecdir}/miredo/
%dir %{_sysconfdir}/miredo
%config(noreplace) %{_sysconfdir}/miredo/miredo.conf
%config(noreplace) %{_sysconfdir}/miredo/client-hook

%pre common
%_pre_useradd miredo /var/empty /bin/true
%_post_service client
%_post_service server
%_preun_service client

%postun common
%_postun_userdel miredo

#----------------------------------------------------------------------------

%prep
%setup -q
%patch0 -p1
%patch1 -p1
%patch2 -p1

%build
autoreconf -fi
%configure2_5x \
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
mkdir -p %{buildroot}%{_unitdir}
install -p -m 644 %{SOURCE1} %{buildroot}%{_unitdir}/miredo-client.service
install -p -m 644 %{SOURCE2} %{buildroot}%{_unitdir}/miredo-server.service
rm -f %{buildroot}%{_libdir}/lib*.la
touch %{buildroot}%{_sysconfdir}/miredo/miredo-server.conf

