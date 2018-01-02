import React from 'react';
import PropTypes from 'prop-types';
import Grid from 'material-ui/Grid';
import { withStyles } from 'material-ui/styles';
import deviceStatus from '../services/deviceStatus';

const styles = () => ({
  root: {
    alignItems: 'center',
    justifyContent: 'center',
    height: '100%',
  },
  item: {
    textAlign: 'center',
  },
});

class DeviceView extends React.Component {
  async componentWillMount() {
    if (await deviceStatus.isRegistered()) {
      // TODO: socket here for sensor stats
    } else {
      this.props.history.replace('/register');
    }
  }

  render() {
    const { classes } = this.props;

    return (
      <Grid container className={classes.root}>
        <Grid item className={classes.item}>
          <h1>Device is registered!</h1>
        </Grid>
      </Grid>
    );
  }
}

DeviceView.propTypes = {
  classes: PropTypes.objectOf(PropTypes.string).isRequired,
  history: PropTypes.object.isRequired,
};

export default withStyles(styles)(DeviceView);