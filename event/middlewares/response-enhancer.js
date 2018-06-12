const responseEnhancer = () => (req, res, next) => {
  res['ok'] = data => {
    const response = { status: 1, data: data }
    console.log('response', response)
    res.json(response);
  }
  res['notok'] = error => {
    const response = { status: 0, message: error.message };
    console.log('response', response)
    res.json(response);
  }
  next();
};

module.exports = responseEnhancer;