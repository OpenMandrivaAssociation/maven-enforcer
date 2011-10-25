%global project_version 1.0-beta-2

Name:           maven-enforcer
Version:        1.0
Release:        0.3.b2
Summary:        Maven Enforcer

Group:          Development/Java
License:        ASL 2.0
URL:            http://maven.apache.org/enforcer
#svn export http://svn.apache.org/repos/asf/maven/enforcer/tags/enforcer-1.0-beta-2 enforcer-1.0-beta-2
#tar caf enforcer-1.0-beta-2.tar.xz enforcer-1.0-beta-2
Source0:        enforcer-%{project_version}.tar.xz
Source1:        %{name}-depmap.xml
Patch0:         fix-site.patch

BuildArch: noarch

BuildRequires: java-devel >= 0:1.6.0

BuildRequires: maven2
BuildRequires: maven-plugin-plugin
BuildRequires: maven-assembly-plugin
BuildRequires: maven-compiler-plugin
BuildRequires: maven-doxia
BuildRequires: maven-doxia-sitetools
BuildRequires: maven-doxia-tools
BuildRequires: maven-install-plugin
BuildRequires: maven-javadoc-plugin
BuildRequires: maven-jar-plugin
BuildRequires: maven-plugin-testing-harness
BuildRequires: maven-plugin-cobertura
BuildRequires: maven-resources-plugin
BuildRequires: maven-site-plugin
BuildRequires: maven-shared-reporting-impl
BuildRequires: maven-surefire-plugin
BuildRequires: maven-surefire-provider-junit
BuildRequires: tomcat6
BuildRequires: plexus-maven-plugin
BuildRequires: plexus-containers-component-javadoc
Requires:      maven2
Requires:       jpackage-utils
Requires:       java
Requires(post):       jpackage-utils
Requires(postun):     jpackage-utils

%description
Enforcer is a build rule execution framework.

%package javadoc
Group:          Development/Java
Summary:        Javadoc for %{name}
Requires:       jpackage-utils

%description javadoc
API documentation for %{name}.

%package api
Summary: Enforcer API
Group: Development/Java
Requires: %{name} = %{version}-%{release}

%description api
This component provides the generic interfaces needed to
implement custom rules for the maven-enforcer-plugin.

%package rules
Summary: Enforcer Rules
Group: Development/Java
Requires: %{name} = %{version}-%{release}
Requires: %{name}-api

%description rules
This component contains the standard Enforcer Rules.

%package -n maven-enforcer-plugin
Summary: Enforcer Rules
Group: Development/Java
Requires: %{name} = %{version}-%{release}
Requires: %{name}-rules
Obsoletes: maven2-plugin-enforcer <= 0:2.0.8
Provides: maven2-plugin-enforcer = 1:%{version}-%{release}

%description -n maven-enforcer-plugin
This component contains the standard Enforcer Rules.


%prep
%setup -q -n enforcer-%{project_version}
%patch0

# fix old dep on javadoc taglet
sed -i 's:<artifactId>plexus-javadoc</artifactId>:<artifactId>plexus-component-javadoc</artifactId>:' pom.xml

%build
export MAVEN_REPO_LOCAL=$(pwd)/.m2/repository
mvn-jpp \
        -e \
        -Dmaven.repo.local=$MAVEN_REPO_LOCAL \
        -Dmaven2.jpp.depmap.file=%{SOURCE1} \
        -Dmaven.test.failure.ignore=true \
        install javadoc:aggregate

%install
# jars
install -d -m 0755 %{buildroot}%{_javadir}/%{name}
install -m 644 enforcer-api/target/enforcer-api-%{project_version}.jar  \
 %{buildroot}%{_javadir}/%{name}/enforcer-api.jar
install -m 644 enforcer-rules/target/enforcer-rules-%{project_version}.jar \
  %{buildroot}%{_javadir}/%{name}/enforcer-rules.jar
install -m 644 maven-enforcer-plugin/target/maven-enforcer-plugin-%{project_version}.jar  \
 %{buildroot}%{_javadir}/%{name}/plugin.jar

# poms
install -d -m 755 $RPM_BUILD_ROOT%{_mavenpomdir}

install -pm 644 pom.xml \
                $RPM_BUILD_ROOT%{_mavenpomdir}/JPP-%{name}.pom
%add_to_maven_depmap org.apache.maven.enforcer enforcer %{project_version} JPP %{name}

install -pm 644 enforcer-api/pom.xml \
                $RPM_BUILD_ROOT%{_mavenpomdir}/JPP.%{name}-enforcer-api.pom
%add_to_maven_depmap org.apache.maven.enforcer enforcer-api %{project_version} JPP/%{name} enforcer-api

install -pm 644 enforcer-rules/pom.xml \
                $RPM_BUILD_ROOT%{_mavenpomdir}/JPP.%{name}-enforcer-rules.pom
%add_to_maven_depmap org.apache.maven.enforcer enforcer-rules %{project_version} JPP/%{name} enforcer-rules

install -pm 644 maven-enforcer-plugin/pom.xml \
                $RPM_BUILD_ROOT%{_mavenpomdir}/JPP.%{name}-plugin.pom
%add_to_maven_depmap org.apache.maven.plugins maven-enforcer-plugin %{project_version} JPP/%{name} plugin

# javadoc
install -d -m 755 %{buildroot}%{_javadocdir}/%{name}
cp -pr target/site/apidocs/* %{buildroot}%{_javadocdir}/%{name}


%post
%update_maven_depmap

%postun
%update_maven_depmap

%pre javadoc
# workaround for rpm bug, can be removed in F-17
[ $1 -gt 1 ] && [ -L %{_javadocdir}/%{name} ] && \
rm -rf $(readlink -f %{_javadocdir}/%{name}) %{_javadocdir}/%{name} || :


%files
%defattr(-,root,root,-)
%dir %{_javadir}/%{name}
%{_mavenpomdir}/*
%{_mavendepmapfragdir}/*

%files javadoc
%defattr(-,root,root,-)
%{_javadocdir}/%{name}

%files api
%defattr(-,root,root,-)
%{_javadir}/%{name}/enforcer-api*

%files rules
%defattr(-,root,root,-)
%{_javadir}/%{name}/enforcer-rules*

%files -n maven-enforcer-plugin
%defattr(-,root,root,-)
%{_javadir}/%{name}/plugin*

