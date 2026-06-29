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
        pending.textContent = data.response || 'No response returned.';
        pending.className = 'srs-chatbot-message srs-chatbot-message-bot';
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
