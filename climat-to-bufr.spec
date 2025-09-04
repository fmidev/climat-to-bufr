%define distnum %(/usr/lib/rpm/redhat/dist.sh --distnum)

%define PACKAGENAME climat-to-bufr
Name:           %{PACKAGENAME}
Version:        0.1.0
Release:        1%{dist}.fmi
Summary:        climat2bufr application
Group:          Applications/System
License:        MIT
URL:            http://www.fmi.fi
Source0: 	%{name}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
Requires:       python3
Requires:       eccodes >= 2.33.0
Requires:       python3-numpy

Provides:	climat2bufr.py

AutoReqProv: no

%global debug_package %{nil}

%description
python tool to create BUFR files from ASCII files

%prep
%setup -q -n "%{PACKAGENAME}"

%build

%install
rm -rf $RPM_BUILD_ROOT
install -m 755 -d %{buildroot}/%{_bindir}
install -m 755 -d %{buildroot}/%{_libdir}/python3.6/site-packages/climat_to_bufr
cp -a *.py %{buildroot}/%{_libdir}/python3.6/site-packages/climat_to_bufr
ln -s %{_libdir}/python3.6/site-packages/climat_to_bufr/climat2bufr.py %{buildroot}/%{_bindir}

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,0755)
%{_libdir}/python3.6/site-packages/climat_to_bufr
%{_bindir}/climat2bufr.py

%changelog
* Thu Sep 04 2025 Tytti Mustonen <tytti.mustonen@fmi.fi> - 0.1.0-1.fmi
- Initial build
