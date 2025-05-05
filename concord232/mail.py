"""
Email notification utilities for concord232. Handles sending system, partition, and log event emails based on configuration.
"""

try:
    import ConfigParser as configparser
except ImportError:
    import configparser
import email
import email.mime
import email.mime.text
import email.utils
import smtplib


class MissingEmailConfig(Exception):
    """Raised when required email configuration is missing."""

    pass


def _send_system_email(config, subject, recips, body):
    """
    Send an email with the given subject and body to the specified recipients using the provided config.
    Args:
        config: ConfigParser object with email settings.
        subject (str): Email subject.
        recips (list): List of recipient email addresses.
        body (str): Email body.
    Raises:
        MissingEmailConfig: If required config options are missing.
    """
    try:
        fromaddr = config.get("email", "fromaddr")
        smtphost = config.get("email", "smtphost")
    except (configparser.NoOptionError, configparser.NoSectionError):
        raise MissingEmailConfig()

    msg = email.mime.text.MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = fromaddr
    msg["Date"] = email.utils.formatdate()
    msg["Message-Id"] = email.utils.make_msgid("concord232")
    for addr in recips:
        msg["To"] = addr

    smtp = smtplib.SMTP(smtphost)
    smtp.sendmail(fromaddr, recips, msg.as_string())
    smtp.quit()


def send_system_email(config, deasserted, asserted):
    """
    Send a system alert email listing asserted and deasserted flags.
    Args:
        config: ConfigParser object with email settings.
        deasserted (set): Flags that are now deasserted.
        asserted (set): Flags that are now asserted.
    """
    try:
        emails = config.get("email", "system").split(",")
    except (configparser.NoOptionError, configparser.NoSectionError):
        return

    if not emails:
        return

    body = (
        "Security System alert.\n"
        + "\n"
        + "The following new flags have been asserted:\n"
        + ("%s\n" % ",".join(asserted))
        + "\n"
        + "The following flags are now de-asserted:\n"
        + ("%s\n" % ",".join(deasserted))
    )

    try:
        _send_system_email(config, "Security System Alert", emails, body)
    except MissingEmailConfig:
        pass


def send_partition_email(config, partition, deasserted, asserted):
    """
    Send a partition alert email for a specific partition, listing asserted and deasserted flags.
    Args:
        config: ConfigParser object with email settings.
        partition: Partition object with a 'number' attribute.
        deasserted (set): Flags that are now deasserted.
        asserted (set): Flags that are now asserted.
    """
    try:
        emails = config.get("partition_%i" % partition.number, "flags").split(",")
    except (configparser.NoOptionError, configparser.NoSectionError):
        return

    try:
        ignore = set(
            config.get("partition_%i" % partition.number, "ignore_flags").split(",")
        )
    except configparser.NoOptionError:
        ignore = set([])

    deasserted = deasserted - ignore
    asserted = asserted - ignore
    if not asserted and not deasserted:
        return
    if not emails:
        return

    body = (
        "Security System partition %i alert.\n" % partition.number
        + "\n"
        + "The following new flags have been asserted:\n"
        + ("%s\n" % ",".join(asserted))
        + "\n"
        + "The following flags are now de-asserted:\n"
        + ("%s\n" % ",".join(deasserted))
    )

    try:
        _send_system_email(
            config,
            "Security System Partition %i Alert" % partition.number,
            emails,
            body,
        )
    except MissingEmailConfig:
        pass


def send_partition_status_email(config, partition, recip_key, sub, message):
    """
    Send a status email for a specific partition with a custom subject and message.
    Args:
        config: ConfigParser object with email settings.
        partition: Partition object with a 'number' attribute.
        recip_key (str): Config key for recipient emails.
        sub (str): Email subject.
        message (str): Email body.
    """
    try:
        emails = config.get("partition_%i" % partition.number, recip_key).split(",")
    except (configparser.NoOptionError, configparser.NoSectionError):
        return

    if not emails:
        return

    body = "Security System alert:\n%s" % message
    try:
        _send_system_email(config, "Security: %s" % sub, emails, body)
    except MissingEmailConfig:
        pass


def send_log_event_mail(config, event):
    """
    Send an email for a log event if it matches configured alarm or event types.
    Args:
        config: ConfigParser object with email settings.
        event: LogEvent object with 'event', 'event_string', and 'timestamp' attributes.
    """
    try:
        alarm_emails = set(config.get("email", "alarms").split(","))
    except (configparser.NoOptionError, configparser.NoSectionError):
        alarm_emails = set([])

    try:
        alarm_events = set(config.get("email", "alarm_events").split(","))
    except (configparser.NoOptionError, configparser.NoSectionError):
        alarm_events = set(
            [
                "Alarm",
                "Alarm restore",
                "Manual fire",
            ]
        )

    try:
        event_emails = set(config.get("email", "events").split(","))
    except (configparser.NoOptionError, configparser.NoSectionError):
        event_emails = set([])

    emails = set(event_emails)
    if event.event in alarm_events:
        emails |= alarm_emails

    if not emails:
        return

    body = "%s at %s" % (event.event_string, event.timestamp)

    _send_system_email(config, "Security: %s" % event.event, emails, body)
