## Overview

- Use [Apache Ivy](http://ant.apache.org/ivy/) to manage build dependencies
- Provide `ivysettings.xml` templates that individual developers can customize based upon their situation.
- Each component repo should include an `ivy.xml` to list dependencies and include a `resolve` target in their `build.xml` that uses `<ivy:resolve>` plus `<ivy:cachepath>` to populate the `class.path` pathid.

## Apache Ivy

Apache Ivy is extremely simple to integrate with out existing and `build.xml` scripts. It uses the following configuration to maintain its local cache of dependencies:

- `ivysettings.xml` (global)
- `ivy.xml` (per-repo)

The default cache location for Ivy is `$HOME/.ivy2/cache`.

## Settings

The main purpose of `ivysettings.xml` as currently used is to define the mechanism or mechanisms used to *resolve* required dependencies.  This is a very flexible mechanism with can pull from Maven repos or even just a local directory.  Here is one example that could be used by a Synacor developer that has internal access:

    <?xml version="1.0" encoding="UTF-8"?>
    <ivysettings>
    <settings defaultResolver="chain-resolver" />
    <property name="archiva-internal"
        value="http://zdev-vm007.eng.zimbra.com:8080/repository/internal" />
    <resolvers>
      <chain name="chain-resolver">
        <filesystem name="local">
          <artifact pattern= "${user.home}/.zcs-deps/[organisation]-[revision].[ext]" />
          <artifact pattern= "${user.home}/.zcs-deps/[organisation].[ext]" />
        </filesystem>
        <ibiblio name="archiva" m2compatible="true" root="${archiva-internal}" />
      </chain>
    </resolvers>
    </ivysettings>


In this example, Ivy will first look in a local directory for dependencies.  In this cases, the location of that (flat) directory is `$HOME/.zcs-deps`.

If the required dependency is not found there, then it will look for dependencies in our internal Maven repo.  You could add one more resolver to the chain that will fall-back to various public Maven repos, but our internal repo is already configured to do that for any dependencies that it does not already have.

## class.path

The repo-specific `ivy.xml` file is where the developer would list the build dependencies. Here is an example file. **Note:** There are more items listed here than would normally be required.

    <?xml version="1.0" encoding="ISO-8859-1"?>
    <ivy-module version="2.0"
     xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
     xsi:noNamespaceSchemaLocation="http://ant.apache.org/ivy/schemas/ivy.xsd">
     <info organisation="com.zimbra" module="zm-bulkprovision-store" status="release">
     </info>
     <dependencies>
      <dependency org="junit" name="junit" rev="4.8.2" />
      <dependency org="servlet-api" name="servlet-api" rev="3.1" />
      <dependency org="dom4j" name="dom4j" rev="1.5.2" />
      <dependency org="guava" name="guava" rev="13.0.1" />
      <dependency org="commons-cli" name="commons-cli" rev="1.2" />
      <dependency org="commons-codec" name="commons-codec" rev="1.7" />
      <dependency org="commons-collections" name="commons-collections" rev="3.2.2" />
      <dependency org="commons-compress" name="commons-compress" rev="1.10" />
      <dependency org="commons-csv" name="commons-csv" rev="1.2" />
      <dependency org="commons-dbcp" name="commons-dbcp" rev="1.4" />
      <dependency org="commons-fileupload" name="commons-fileupload" rev="1.2.2" />
      <dependency org="commons-httpclient" name="commons-httpclient" rev="3.1" />
      <dependency org="commons-io" name="commons-io" rev="1.4" />
      <dependency org="commons-lang" name="commons-lang" rev="2.6" />
      <dependency org="commons-logging" name="commons-logging" rev="1.0" />
      <dependency org="commons-net" name="commons-net" rev="3.3" />
      <dependency org="commons-pool" name="commons-pool" rev="1.6" />
      <dependency org="zimbra-charset" name="zimbra-charset" rev="1.0" />
      <dependency org="zimbraclient" name="zimbraclient" rev="1.0" />
      <dependency org="zimbracmbsearch" name="zimbracmbsearch" rev="1.0" />
      <dependency org="zimbracommon" name="zimbracommon" rev="1.0" />
      <dependency org="zimbra-license-tools" name="zimbra-license-tools" rev="1.0" />
      <dependency org="zimbra-native" name="zimbra-native"  rev="1.0" />
      <dependency org="zimbrasoap" name="zimbrasoap" rev="1.0" />
      <dependency org="zimbrastore" name="zimbrastore" rev="1.0" />
     </dependencies>
    </ivy-module>

A couple of items to note.

- The `rev` attribute is required.  For dependencies that do not currently contain version information, I have just put `rev="1.0"` as the attribute.
- As we update our builds to correctly version our ZCS dependencies, we would update that attribute to contain the *actual* correct version number.
- The example *resolver* shown above that pulls from a flat local directory contains an artifact pattern that will allow resolution to jar files that do not contain version information.

