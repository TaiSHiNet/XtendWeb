#!/usr/bin/env python


import yaml
import argparse
import os
import sys
import pwd
try:
    import simplejson as json
except ImportError:
    import json


__author__ = "Anoop P Alias"
__copyright__ = "Copyright Anoop P Alias"
__license__ = "GPL"
__email__ = "anoopalias01@gmail.com"


installation_path = "/opt/nDeploy"  # Absolute Installation Path
nginx_bin = "/usr/sbin/nginx"
app_signatures = installation_path+"/conf/appsignatures.yaml"
# Function defs


def set_preferred_php():
    backend_config_file = installation_path+"/conf/backends.yaml"
    backend_data_yaml = open(backend_config_file, 'r')
    backend_data_yaml_parsed = yaml.safe_load(backend_data_yaml)
    backend_data_yaml.close()
    if "PHP" in backend_data_yaml_parsed:
        print("Please choose one preferred PHP version from the list below")
        php_backends_dict = backend_data_yaml_parsed["PHP"]
        for versions_defined in list(php_backends_dict.keys()):
            print(versions_defined)
        try:
            input = raw_input
        except NameError:
            pass
        myinput = input("Provide the exact desired version string here and press ENTER: ")
        required_version = str(myinput)
        required_version_path = php_backends_dict.get(required_version)
        userdata_dict = {'PHP': {required_version: required_version_path}}
        with open(installation_path+"/conf/preferred_php.yaml", 'w') as yaml_file:
            yaml.dump(userdata_dict, yaml_file, default_flow_style=False)
        return
    else:
        print("ERROR : You need atleast one PHP backends defined")
        sys.exit(1)


def nginx_conf_switch(user_name, domain_name):
    cpdomainjson = "/var/cpanel/userdata/" + user_name + "/" + domain_name + ".cache"
    if os.path.isfile(cpdomainjson):
        with open(cpdomainjson, 'r') as cpaneldomain_data_stream:
            json_parsed_cpaneldomain = json.load(cpaneldomain_data_stream)
        document_root = json_parsed_cpaneldomain.get('documentroot')
        if domain_name.startswith('*'):
            domain_data_file = installation_path+"/domain-data/"+"_wildcard_."+domain_name.replace('*.', '')
        else:
            domain_data_file = installation_path+"/domain-data/"+domain_name
        if os.path.isfile(domain_data_file):
            with open(domain_data_file, 'r') as domaindata_data_stream:
                yaml_parsed_domaindata = yaml.safe_load(domaindata_data_stream)
            backend_category = yaml_parsed_domaindata.get('backend_category')
            if backend_category == "PROXY":
                phpsigs = yaml_parsed_sigs.get("PHP")
                for app_path in list(phpsigs.keys()):
                    if os.path.isfile(document_root+app_path):
                        yaml_parsed_domaindata["backend_category"] = "PHP"
                        yaml_parsed_domaindata["backend_version"] = my_phpversion
                        yaml_parsed_domaindata["backend_path"] = my_phppath
                        yaml_parsed_domaindata["apptemplate_code"] = phpsigs.get(app_path)
                        with open(domain_data_file, 'w') as yaml_file:
                            yaml.dump(yaml_parsed_domaindata, yaml_file, default_flow_style=False)
                        yaml_file.close()
        else:
            print("Error loading domain-data file for domain: "+domain_name)
    else:
        print("Error loading userdata file for domain: "+domain_name)

    # End Function defs


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Auto switch nginx config for domains of a cpanel user")
    parser.add_argument("CPANELUSER")
    args = parser.parse_args()
    cpaneluser = args.CPANELUSER
    if os.path.isfile(installation_path+"/conf/auto_config.exclude"):
        with open(installation_path+"/conf/auto_config.exclude") as excludes:
            for line in excludes:
                if str(line).rstrip() == cpaneluser:
                    sys.exit(0)
    try:
        pwd.getpwnam(cpaneluser)
    except KeyError:
        sys.exit(0)
    else:
        cpuserdatajson = "/var/cpanel/userdata/" + cpaneluser + "/main.cache"
        if os.path.isfile(cpuserdatajson):
            with open(cpuserdatajson) as cpaneluser_data_stream:
                json_parsed_cpaneluser = json.load(cpaneluser_data_stream)
            main_domain = json_parsed_cpaneluser.get('main_domain')
            # parked_domains = yaml_parsed_cpaneluser.get('parked_domains')   #This data is irrelevant as parked domain list is in ServerAlias
            # addon_domains = yaml_parsed_cpaneluser.get('addon_domains')     #This data is irrelevant as addon is mapped to a subdomain
            sub_domains = json_parsed_cpaneluser.get('sub_domains')
            # Get the appsignatures and preferred php details
            if not os.path.isfile(installation_path+"/conf/preferred_php.yaml"):
                set_preferred_php()
            prefphpyaml = installation_path+"/conf/preferred_php.yaml"
            with open(prefphpyaml, 'r') as prefphpyaml_data_stream:
                yaml_parsed_prefphpyaml = yaml.safe_load(prefphpyaml_data_stream)
            phpversion = yaml_parsed_prefphpyaml.get('PHP')
            my_phpversion = str(phpversion.keys()[0])
            my_phppath = str(phpversion.get(my_phpversion))
            sigsyaml = installation_path+"/conf/appsignatures.yaml"
            with open(sigsyaml, 'r') as sigs_data_stream:
                yaml_parsed_sigs = yaml.safe_load(sigs_data_stream)
            nginx_conf_switch(cpaneluser, main_domain)  # Generate conf for main domain

            for domain_in_subdomains in sub_domains:
                nginx_conf_switch(cpaneluser, domain_in_subdomains)  # Generate conf for sub domains which takes care of addon as well
        else:
            print("Error loading userdata file for user: "+cpaneluser)
