(function () {
  var root = document.querySelector('.srs-chatbot');
  if (!root) {
    return;
  }

  var toggle = root.querySelector('.srs-chatbot-toggle');
  var minimize = root.querySelector('.srs-chatbot-minimize');
  var windowEl = root.querySelector('.srs-chatbot-window');
  var form = root.querySelector('.srs-chatbot-form');
  var input = root.querySelector('#srs-chatbot-input');
  var messages = root.querySelector('.srs-chatbot-messages');
  var options = root.querySelectorAll('.srs-chatbot-option');
  var timestamp = root.querySelector('.srs-chatbot-timestamp');
  var csrfInput = root.querySelector('input[name="csrfmiddlewaretoken"]');
  var endpoint = root.getAttribute('data-chatbot-endpoint');

  function formatTimestamp(date) {
    var month = date.toLocaleString('en-US', { month: 'long' });
    var day = date.getDate();
    var hours = date.getHours();
    var minutes = String(date.getMinutes()).padStart(2, '0');
    var period = hours >= 12 ? 'PM' : 'AM';

    hours = hours % 12 || 12;
    return month + ' ' + day + ', ' + hours + ':' + minutes + ' ' + period;
  }

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
    message.className = 'srs-chatbot-message srs-chatbot-message-dynamic srs-chatbot-message-' + sender;
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
    if (url.indexOf('mailto:') !== 0) {
      link.target = '_blank';
      link.rel = 'noopener noreferrer';
    }
    return link;
  }

  function splitTrailingUrlPunctuation(url) {
    var match = url.match(/^(.+?)([.,;:!?]+)$/);
    if (!match) {
      return {
        url: url,
        suffix: ''
      };
    }

    return {
      url: match[1],
      suffix: match[2]
    };
  }

  function appendResponseLink(element, url, label) {
    var cleanedUrl = splitTrailingUrlPunctuation(url);
    element.appendChild(createResponseLink(cleanedUrl.url, label));
    if (cleanedUrl.suffix) {
      element.appendChild(document.createTextNode(cleanedUrl.suffix));
    }
  }

  function joinBrokenMarkdownText(wordFragment, labelPrefix) {
    if (!wordFragment) {
      return labelPrefix;
    }
    if (wordFragment.length <= 3 && /^[a-z]/.test(labelPrefix)) {
      return wordFragment + labelPrefix;
    }
    if (/^or\b/i.test(labelPrefix)) {
      return wordFragment + ' ' + labelPrefix;
    }
    return wordFragment + labelPrefix;
  }

  function normalizeResponseText(text) {
    return text
      .replace(/\\n/g, '\n')
      .replace(/\\([\[\]()])/g, '$1')
      .replace(/(\w*)\[([\s\S]*?(?:official\s+)?help page[\s\S]*?)\]\(\s*(https?:\/\/srs\.it\.umich\.edu\/help[^)]*)\s*\)/gi, function (fullMatch, wordFragment, label, url) {
        var labelParts = label.match(/^([\s\S]*?)(official help page|help page)([\s\S]*)$/i);
        if (!labelParts) {
          return fullMatch;
        }
        return joinBrokenMarkdownText(wordFragment, labelParts[1]) + '[' + labelParts[2] + '](' + url + ')' + labelParts[3];
      });
  }

  function splitTrailingLinkLabel(text) {
    var preferredMatch = text.match(/^([\s\S]*?\b)(direct link|learn more here|more details here|official documentation|documentation|here):\s*$/i);
    var match = text.match(/^([\s\S]*?)([^.!?\n]{3,80}):\s*$/);
    var label;

    if (preferredMatch) {
      label = preferredMatch[2].trim();
      if (label.toLowerCase() === 'documentation') {
        label = 'official documentation';
      }
      return {
        prefix: preferredMatch[1],
        label: label
      };
    }

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
    return /^(source|link|url)$/i.test(label.trim()) || /^https?:\/\//i.test(label.trim());
  }

  function getGenericLinkLabel(url) {
    if (url.indexOf('documentation.its.umich.edu') !== -1) {
      return 'learn more here';
    }
    if (url.indexOf('srs.it.umich.edu/help') !== -1) {
      return 'SRS help page';
    }
    if (url.indexOf('srs.it.umich.edu') !== -1) {
      return 'SRS';
    }
    return 'source';
  }

  function splitVerboseMarkdownLabel(label, url) {
    var match;

    if (url.indexOf('srs.it.umich.edu/help') === -1) {
      return null;
    }

    match = label.match(/^([\s\S]*?)(official help page|help page)([\s\S]*)$/i);
    if (!match) {
      return null;
    }

    return {
      prefix: match[1],
      label: match[2],
      suffix: match[3]
    };
  }

  function appendLinkedText(element, text) {
    var linkPattern = /\[([\s\S]*?)\]\(\s*(https?:\/\/[^)]+?)\s*\)|(https?:\/\/[^\s<>"']+)|([A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,})/gi;
    var lastIndex = 0;
    var match;
    var textBeforeLink;
    var trailingLabel;

    text = normalizeResponseText(text);
    element.textContent = '';
    while ((match = linkPattern.exec(text)) !== null) {
      textBeforeLink = text.slice(lastIndex, match.index);

      if (match[1] && match[2]) {
        trailingLabel = isGenericLinkLabel(match[1]) ? splitTrailingLinkLabel(textBeforeLink) : null;
        if (trailingLabel) {
          element.appendChild(document.createTextNode(trailingLabel.prefix));
          appendResponseLink(element, match[2], trailingLabel.label);
        } else if (isGenericLinkLabel(match[1])) {
          element.appendChild(document.createTextNode(textBeforeLink));
          appendResponseLink(element, match[2], getGenericLinkLabel(match[2]));
        } else {
          trailingLabel = splitVerboseMarkdownLabel(match[1], match[2]);
          element.appendChild(document.createTextNode(textBeforeLink));
          if (trailingLabel) {
            element.appendChild(document.createTextNode(trailingLabel.prefix));
            appendResponseLink(element, match[2], trailingLabel.label);
            if (trailingLabel.suffix) {
              element.appendChild(document.createTextNode(trailingLabel.suffix));
            }
          } else {
            appendResponseLink(element, match[2], match[1]);
          }
        }
      } else if (match[3]) {
        trailingLabel = splitTrailingLinkLabel(textBeforeLink);
        if (trailingLabel) {
          element.appendChild(document.createTextNode(trailingLabel.prefix));
          appendResponseLink(element, match[3], trailingLabel.label);
        } else {
          element.appendChild(document.createTextNode(textBeforeLink));
          appendResponseLink(element, match[3], getGenericLinkLabel(match[3]));
        }
      } else {
        element.appendChild(document.createTextNode(textBeforeLink));
        element.appendChild(createResponseLink('mailto:' + match[4], match[4]));
      }

      lastIndex = linkPattern.lastIndex;
    }

    element.appendChild(document.createTextNode(text.slice(lastIndex)));
  }

  function setBusy(isBusy) {
    form.querySelector('button[type="submit"]').disabled = isBusy;
    input.disabled = isBusy;
    Array.prototype.forEach.call(options, function (option) {
      option.disabled = isBusy;
    });
  }

  function sendMessage(query) {
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
        pending.className = 'srs-chatbot-message srs-chatbot-message-dynamic srs-chatbot-message-bot';
        appendLinkedText(pending, data.response || 'No response returned.');
      })
      .catch(function (error) {
        pending.textContent = error.message;
        pending.className = 'srs-chatbot-message srs-chatbot-message-dynamic srs-chatbot-message-error';
      })
      .finally(function () {
        setBusy(false);
        input.focus();
      });
  }

  toggle.addEventListener('click', function () {
    setOpen(windowEl.hidden);
  });

  if (minimize) {
    minimize.addEventListener('click', function () {
      setOpen(false);
    });
  }

  Array.prototype.forEach.call(options, function (option) {
    option.addEventListener('click', function () {
      sendMessage(option.getAttribute('data-prompt'));
    });
  });

  if (timestamp) {
    timestamp.textContent = formatTimestamp(new Date());
  }

  form.addEventListener('submit', function (event) {
    event.preventDefault();

    // User input starts here, then gets posted to Django's /chatbot/message/ endpoint.
    var query = input.value.trim();
    if (!query) {
      return;
    }

    sendMessage(query);
  });
}());
