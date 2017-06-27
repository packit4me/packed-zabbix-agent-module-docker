%{!?source_ref: %global source_ref master}
%{!?zabbix_version: %global zabbix_version 3.2.6}

%global selinux_variants mls targeted

%define upstream_name zabbix-docker-monitoring


Name:           zabbix-agent-module-docker
Version:        1.1
Release:        1%{?dist}
Summary:        Zabbix Agent extension module that supports Docker

License:        GPLv2
URL:            https://github.com/monitoringartist/%{upstream_name}
# Our first source is the Zabbix source code, because the libraries are required
# to build the module but are not provided in any other consumable manner
Source0:        https://downloads.sourceforge.net/project/zabbix/ZABBIX%20Latest%20Stable/%{zabbix_version}/zabbix-%{zabbix_version}.tar.gz
Source1:        https://github.com/monitoringartist/%{upstream_name}/archive/%{source_ref}.zip

BuildRequires:  checkpolicy
BuildRequires:  selinux-policy-devel
BuildRequires:  hardlink

Requires:       zabbix-agent
%if "%{_selinux_policy_version}" != ""
Requires:       selinux-policy >= %{_selinux_policy_version}
%endif

%description


%prep
%setup -n zabbix-%{zabbix_version}
#./bootstrap.sh
cd -
%setup -T -b 1 -n %{upstream_name}-%{source_ref}
cd -
mkdir -p zabbix-%{zabbix_version}/src/modules/zabbix_module_docker
cp %{upstream_name}-%{source_ref}/src/modules/zabbix_module_docker/* zabbix-%{zabbix_version}/src/modules/zabbix_module_docker
#cp %{upstream_name}-%{source_ref}/LICENSE LICENSE

%build
cd -
cd zabbix-%{zabbix_version}
%configure --enable-agent
cd src/modules/zabbix_module_docker
%make_build
cd ../../../..
cd %{upstream_name}-%{source_ref}/selinux
for selinuxvariant in %{selinux_variants}
do
  make NAME=${selinuxvariant} -f /usr/share/selinux/devel/Makefile
  mv zabbix-docker.pp zabbix-docker.pp.${selinuxvariant}
  make NAME=${selinuxvariant} -f /usr/share/selinux/devel/Makefile clean
done

%install
rm -rf %{buildroot}
cd ..
mkdir -p %{buildroot}%{_libdir}/zabbix/modules/
cp zabbix-%{zabbix_version}/src/modules/zabbix_module_docker/zabbix_module_docker.so %{buildroot}%{_libdir}/zabbix/modules/
cd %{upstream_name}-%{source_ref}
for selinuxvariant in %{selinux_variants}
do
  install -d %{buildroot}%{_datadir}/selinux/${selinuxvariant}
  install -p -m 644 selinux/zabbix-docker.pp.${selinuxvariant} \
    %{buildroot}%{_datadir}/selinux/${selinuxvariant}/zabbix-docker.pp
done
/usr/sbin/hardlink -cv %{buildroot}%{_datadir}/selinux

%post
for selinuxvariant in %{selinux_variants}
do
  /usr/sbin/semodule -s ${selinuxvariant} -i \
    %{_datadir}/selinux/${selinuxvariant}/%{modulename}.pp &> /dev/null || :
done
/sbin/fixfiles -R myapp restore || :

%postun
if [ $1 -eq 0 ] ; then
  for selinuxvariant in %{selinux_variants}
  do
    /usr/sbin/semodule -s ${selinuxvariant} -r %{modulename} &> /dev/null || :
  done
fi

%files
%defattr(-,root,root,0755)
%license LICENSE
%doc CHANGELOG.md README.md
%{_libdir}/zabbix/modules/zabbix_module_docker.so
%{_datadir}/selinux/*/zabbix-docker.pp

%changelog
* Mon Apr  3 2017 Greg Swift <gregswift@gmail.com> - 1.1-1
- Initial version
