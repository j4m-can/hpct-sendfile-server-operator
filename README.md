# hpct-sendfile-server-operator

## Description

The `hpct-sendfile-server-operator` and `hpct-sendfile-client-operator`
pair of operators work together to demonstrate how the `FileDataInteface`
can be used for sending files between units.

## Usage

Start operators:

```
juju deploy ./hpct-sendfile-server-operator_ubuntu-22.04-amd64.charm sendfile-server
juju deploy ./hpct-sendfile-client-operator_ubuntu-22.04-amd64.charm senffile-client
```

Set up relation:

```
juju relate sendfile-server:sendfile sendfile-client:sendfile
```

Send a file (only possible from the server):

```
juju run-action sendfile-server/leader send-file filename=/etc/hosts
```

At which point,

1. the `/etc/hosts` file, along with its metadata, will be
copied into the unit data bucket
1. all other units will be notified with a relation-changed event
1. the client will look into the data bucket "sending" unit for the file
data and copy it to a `SAVEDIR` location (e.g., `/tmp/sendfile-client`)
1. the client will write an acknowledgement to its own bucket
1. an relation-changed event will be sent to the server
1. the server will clear the file.nonce setting to indicate that the
file was picked up

## Relations

Client:

```
requires:
  sendfile:
    interface: sendfile
```

Server:

```
provides:
  sendfile:
    interface: sendfile
    limit: 1
```

## Contributing

Please see the [Juju SDK docs](https://juju.is/docs/sdk) for guidelines
on enhancements to this charm following best practice guidelines, and
`CONTRIBUTING.md` for developer guidance.
