(function () {
  var root = document.querySelector('.srs-chatbot');
  if (!root) {
    return;
  }

  var toggle = root.querySelector('.srs-chatbot-toggle');
  var close = root.querySelector('.srs-chatbot-close');
  var windowEl = root.querySelector('.srs-chatbot-window');
  var form = root.querySelector('.srs-chatbot-form');
  var input = root.querySelector('#srs-chatbot-input');
  var messages = root.querySelector('.srs-chatbot-messages');
  var csrfInput = root.querySelector('input[name="csrfmiddlewaretoken"]');
  var endpoint = root.getAttribute('data-chatbot-endpoint');

  function setOpen(isOpen) {
    windowEl.hidden = !isOpen;
    toggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
    if (isOpen) {
      input.focus();
    } else {
      toggle.focus();
    }
  }

  function appendMessage(text, sender) {
    var message = document.createElement('div');
    message.className = 'srs-chatbot-message srs-chatbot-message-' + sender;
    // Use textContent so chatbot/user text is displayed as text, not executable HTML.
    message.textContent = text;
    messages.appendChild(message);
    messages.scrollTop = messages.scrollHeight;
    return message;
  }

  function createResponseLink(url, label) {
    var link = document.createElement('a');
    link.href = url;
    link.textContent = label || url;
    link.target = '_blank';
    link.rel = 'noopener noreferrer';
    return link;
  }

  function splitTrailingLinkLabel(text) {
    var match = text.match(/^(.*?)([^.!?\n]{3,80}):\s*$/);
    var label;

    if (!match) {
      return null;
    }

    label = match[2].trim();
    if (label.toLowerCase().indexOf('documentation') !== -1) {
      label = 'official documentation';
    }

    return {
      prefix: match[1],
      label: label
    };
  }

  function isGenericLinkLabel(label) {
    return /^(source|link|url)$/i.test(label.trim());
  }

  function appendLinkedText(element, text) {
    var linkPattern = /\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)|(https?:\/\/[^\s<>"']+)/g;
    var lastIndex = 0;
    var match;
    var textBeforeLink;
    var trailingLabel;

    element.textContent = '';
    while ((match = linkPattern.exec(text)) !== null) {
      textBeforeLink = text.slice(lastIndex, match.index);

      if (match[1] && match[2]) {
        trailingLabel = isGenericLinkLabel(match[1]) ? splitTrailingLinkLabel(textBeforeLink) : null;
        if (trailingLabel) {
          element.appendChild(document.createTextNode(trailingLabel.prefix));
          element.appendChild(createResponseLink(match[2], trailingLabel.label));
        } else {
          element.appendChild(document.createTextNode(textBeforeLink));
          element.appendChild(createResponseLink(match[2], match[1]));
        }
      } else {
        trailingLabel = splitTrailingLinkLabel(textBeforeLink);
        if (trailingLabel) {
          element.appendChild(document.createTextNode(trailingLabel.prefix));
          element.appendChild(createResponseLink(match[3], trailingLabel.label));
        } else {
          element.appendChild(document.createTextNode(textBeforeLink));
          element.appendChild(createResponseLink(match[3], 'source'));
        }
      }

      lastIndex = linkPattern.lastIndex;
    }

    element.appendChild(document.createTextNode(text.slice(lastIndex)));
  }

  function setBusy(isBusy) {
    form.querySelector('button[type="submit"]').disabled = isBusy;
    input.disabled = isBusy;
  }

  toggle.addEventListener('click', function () {
    setOpen(windowEl.hidden);
  });

  close.addEventListener('click', function () {
    setOpen(false);
  });

  form.addEventListener('submit', function (event) {
    event.preventDefault();

    // User input starts here, then gets posted to Django's /chatbot/message/ endpoint.
    var query = input.value.trim();
    if (!query) {
      return;
    }

    appendMessage(query, 'user');
    input.value = '';
    setBusy(true);
    var pending = appendMessage('Waiting for response...', 'system');

    fetch(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        // Django's CSRF token is required because the endpoint changes server-side state.
        'X-CSRFToken': csrfInput ? csrfInput.value : ''
      },
      body: JSON.stringify({ query: query })
    })
      .then(function (response) {
        return response.json().then(function (data) {
          if (!response.ok) {
            throw new Error(data.error || 'Unable to send message.');
          }
          return data;
        });
      })
      .then(function (data) {
        pending.className = 'srs-chatbot-message srs-chatbot-message-bot';
        appendLinkedText(pending, data.response || 'No response returned.');
      })
      .catch(function (error) {
        pending.textContent = error.message;
        pending.className = 'srs-chatbot-message srs-chatbot-message-error';
      })
      .finally(function () {
        setBusy(false);
        input.focus();
      });
  });
}());
