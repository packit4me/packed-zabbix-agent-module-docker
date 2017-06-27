%{!?source_ref: %global source_ref master}
%{!?zabbix_version: %global zabbix_version 3.2.6}

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

Requires:       zabbix-agent

%description


%prep
%setup -n zabbix-%{zabbix_version}
#./bootstrap.sh
cd ..
%setup -T -b 1 -n %{upstream_name}-%{source_ref}
cd ..
mkdir -p zabbix-%{zabbix_version}/src/modules/zabbix_module_docker
cp %{upstream_name}-%{source_ref}/src/modules/zabbix_module_docker/* zabbix-%{zabbix_version}/src/modules/zabbix_module_docker
#cp %{upstream_name}-%{source_ref}/LICENSE LICENSE

%build
cd ..
cd zabbix-%{zabbix_version}
%configure --enable-agent
cd src/modules/zabbix_module_docker
%make_build

%install
rm -rf %{buildroot}
cd ..
mkdir -p %{buildroot}%{_libdir}/zabbix/modules/
cp zabbix-%{zabbix_version}/src/modules/zabbix_module_docker/zabbix_module_docker.so %{buildroot}%{_libdir}/zabbix/modules/
#checkmodule -M -m -o zabbix-docker.mod zabbix-docker.te
#semodule_package -o zabbix-docker.pp -m zabbix-docker.mod

%post
#usermod -aG docker zabbix
#semodule -i zabbix-docker.pp

%files
%license LICENSE
%doc README.md
%{_libdir}/zabbix/modules/zabbix_module_docker.so


%changelog
* Mon Apr  3 2017 xaeth <gregswift@gmail.com>
- 
