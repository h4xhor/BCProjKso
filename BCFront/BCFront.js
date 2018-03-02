const DOMAIN = 'https://8t86re13ai.execute-api.ap-southeast-2.amazonaws.com/dev'

// for testing locallh
//const DOMAIN = 'http://localhost:8081'

const ERROR = 'ERROR'
const OK = 'OK'

const FIELDS = 'fields'
const NAME = 'name'

// for rows and all_risks_with_fields
const TYPE = 'type'

// for JSON object with back end.
const RISK_TYPE = 'risk_type'

const VAL = 'val'
const ALL_RISKS = 'all_risks'

const UNDEFINED = 'undefined'

const TRUE_STR = 'True'
const FALSE_STR = 'False'

// seconds to hit JWT exp (30 minutes)
const EXP_MARGIN = 1800

// time from JWT originally issued at time (seconds) for refreshing JWT
// 7 days - 30 minutes = 7*24*60*60 - 30*60 seconds
//                     = 604800 - 1800
//                     = 603000
const IAT_DUR = 603000

// ref https://hackernoon.com/jwt-authentication-in-vue-js-and-django-rest-framework-part-2-788f0ad53ad5
const store = new Vuex.Store({
  state: {
    // allows persistence of the token with page refreshes
    jwt: localStorage.getItem('t'),
    isLoggedIn: localStorage.getItem('isLoggedIn'),

    endpoints: {
      obtainJWT: DOMAIN + '/genRisks/auth/obtain_token/',
      refreshJWT: DOMAIN + '/genRisks/auth/refresh_token/'
    }
  },

  // getters
  getters: {
    isLoggedIn: state => {
      if (state.jwt) {
        return true
      } else {
        return false
      }
    },

    token_obj: state => {
      if (state.jwt) {
        const token = state.jwt;
        console.log('token = ' + token)

        try {

          decoded = JSON.parse(atob(token.split('.')[1]))
          console.log('dec = ' + JSON.stringify(decoded))

          return decoded;
        } catch (e) {
          console.log('c')
          return null;
        }
        console.log('d')
      }
    }
  },

  // invoke via this.commit()
  mutations: {
    updateToken(state, newToken){

      localStorage.setItem('t', newToken);
      state.jwt = newToken;

      localStorage.setItem('isLoggedIn', true),
      state.isLoggedIn = true
    },

    removeToken(state){
      localStorage.removeItem('t');
      state.jwt = null;

      localStorage.removeItem('isLoggedIn'),
      state.isLoggedIn = false

    }
  },

  // invoke asynchronous actions via dispatch()
  // ref [https://stackoverflow.com/questions/40165766/returning-promises-from-vuex-actions]
  actions: {

    obtainToken(context, payload) {
      return new Promise((resolve, reject) => {
        const json_obj = {
          'username': payload.uname,
          'password': payload.pw
        }

        url = this.state.endpoints.obtainJWT
        console.log('uname = ' + payload.uname + ', pw = ' + payload.pw)

        Vue.http.post(url, 
          json_obj, 
          {headers: {'Content-Type': 'application/json'}}).then(response => {

            this.commit('updateToken', response.data.token);
            console.log('tok = ' + response.data.token)
            console.log(OK + ': got new token')
            this.state.isLoggedIn = true

            resolve(response) 

          }, error => {
            this.state.isLoggedIn = false
            console.log(ERROR + ': failed to get new token')

            reject(error)
        })
      })
    },

    refreshToken() {
      return new Promise((resolve, reject) => {
        const json_obj = {
          token: this.state.jwt
        }

        url = this.state.endpoints.refreshJWT
        
        Vue.http.post(url, 
          json_obj,
          {headers: {'Content-Type': 'application/json'}}).then(response => {

            this.commit('updateToken', response.data.token);
            console.log('tok = ' + response.data.token)
            console.log(OK + ': refreshed token')

            resolve(response)
          }, error => {
            console.log(ERROR + ': failed to refresh token')
            reject(error)
        })
      })
    },

    inspectToken() {
      return new Promise((resolve, reject) => {
        token_obj = this.getters.token_obj
        if(token_obj) {

          // expiry (seconds)
          const exp = token_obj.exp

          // originally issued at (seconds)
          const orig_iat = token_obj.orig_iat

          const secs_now = Date.now()/1000
          tot_secs_left = exp - secs_now 

          hrs_left = Math.trunc(tot_secs_left / (60*60))
          mins_left = Math.trunc(tot_secs_left / 60) % 60
          secs_left = Math.round(tot_secs_left % 60)
          console.log('token time to expiry = ' + hrs_left + ' hrs ' + 
            mins_left + ' mins ' + secs_left + ' secs.')

          if (secs_now > exp) {
            // expired, relogin
            this.commit('removeToken')
            console.log('token expired')

          } else if ((exp - secs_now < EXP_MARGIN) &&
                     (secs_now - orig_iat < IAT_DUR)) {
            // < 30 minutes before hitting exp and
            // 30 minutes before reaching orig_iat + 7 days
            this.dispatch('refreshToken').then(response => {
              resolve(response)
            }, error => {
              reject(error)
            })

          } else {
            console.log('waiting for token expiry')
            // wait for expiry
          }
        }
      })
    }

  } // actions

})


var app = new Vue({
  el: "#app",

  // state
  data: {
    username: '',
    password: '',
    is_admin: false,

    num_users: 0,

    use_case: '',
    new_username: '',
    new_pw: '',
    new_user_is_admin: false,
    is_admin_text: 'no',

    existing_users: [],
    // in the case of a non admin user, user_to_show == username
    // admin users can see all existing users
    user_to_show: '',

    risk_type: '',

    /* In rows, the 2nd last field are  booleans for enabling use of the 
     * Save Field button 
     * true for disabled, false for enabled
     *
     * These are for existing fields
     *
     * The last field is for newly added rows.
     * true for newly added, false for existing items.
     * Users can only alter the name and type for newly added rows.
     *
     */
    rows: [],

    /* To easily test creation of new risk: 
     * 1. Paste contents of rows_test into this.rows and 
     * 2. Set this.use_case = 'create_risk'
     */
    /*rows_test: [{'name': 'make', 'type': 'text', 'val': 'Toyota', 'saveButDis': true, 'notNew': false},
      {'name': 'model', 'type': 'text', 'val': 'Corolla', 'saveButDis': true, 'notNew': false},
      {'name': 'num_cylinders', 'type': 'number', 'val': '4', 'saveButDis': true, 'notNew': false},
      {'name': 'num_doors', 'type': 'number', 'val': '5', 'saveButDis': true, 'notNew': false},
      {'name': 'value', 'type': 'currency', 'val': '2000', 'saveButDis': true, 'notNew': false},
      {'name': 'date_manufacture', 'type': 'date', 'val': '2017-09-03', 'saveButDis': true, 'notNew': false},
      {'name': 'date_owned', 'type': 'date', 'val': '2018-02-02', 'saveButDis': true, 'notNew': false},
      {'name': 'amount_insured', 'type': 'currency', 'val': '2000', 'saveButDis': true, 'notNew': false}],*/


    field_types: ['text', 
            'number',
            'currency',
            'date'],

    existing_risks: [],

    /* Format of all_risks_with_fields:
     *
     * [
     *   {"risk_type": "risk0",
     *   "fields": [{"name": "make0", "type": "text", "val": "Toyota0" },
     *              {"name": "num_doors0", "type": "number", "val": "50" }]
     *    },
     *    {"risk_type": "risk1",
     *   "fields": [{"name": "make1", "type": "text", "val": "Toyota1" },
     *              {"name": "num_doors1", "type": "number", "val": "50" }]
     *    },
     *    {"risk_type": "risk2",
     *   "fields": [{"name": "make2", "type": "text", "val": "Toyota2" },
     *              {"name": "num_doors2", "type": "number", "val": "52" }]
     *    }
     * ]
     */
    all_risks_with_fields: [],

    risk_type: '',

    sending: '',
    status_msg: ''
  },

  // computed properties
  computed: {
    createFirstUser() {
      if (0 == this.num_users) {
        this.status_msg = 'Please create a first user. Admin privileges will be given.'
        return true

      } else {
        return false
      }
    },

    isLoggedIn() {
      if (store.getters.isLoggedIn) {
        this.password = ''

        // once we've got the token, get the username 
        this.getTokenUname()

        // update is_admin.
        this.isAdmin()

      }
      return store.getters.isLoggedIn
    },

    isCreateUser: function() {
      return "create_user" == this.use_case
    },

    isDelUser: function() {
      return "del_user" == this.use_case
    },

    isCreateRisk: function() {
      if ("create_risk" == this.use_case) {
        return true

      } else {
        return false
      }
    },

    isEditRisk: function() {
      if ('edit_risk' == this.use_case) {
        return true
      } else {
        return false
      }
    },

    isEditOrCreateRisk: function() {
      return (this.isEditRisk || this.isCreateRisk)
    },

    isShowAllRisks: function() {
      return ('show_all_risks' == this.use_case)
    },

    desc: function() {
      msg = ''
      if (this.isCreateUser) {
        msg = "Creates a new user and saves to database."
      } else if (this.isDelUser) {
        msg = "Deletes an existing user."
      } else if (this.isCreateRisk) {
        msg = "Creates a new risk type for an existing user."
      } else if (this.isEditRisk) {
        msg = "Edit or delete an existing risk type (for an existing user)."
      } else if (this.isShowAllRisks) {
        msg = 'Shows all risk types and their fields'
      } else {
        msg = ERROR + ': Non existent mode'
      }

      return msg
    }

  },

  methods: {
    login() {
      if (0 == this.username.length) {
        this.status_msg = 'Username can not be empty!'
      } else if (0 == this.password.length) {
        this.status_msg = 'Password can not be empty!'
      } else {

        console.log('username = ' + this.username + ', password = ' + this.password)
        store.dispatch('obtainToken', {
          uname: this.username, 
          pw: this.password,
        }).then(response => {
          
        }, error => {
          if (false == store.state.isLoggedIn) {
            this.status_msg = ERROR + ': Incorrect credentials'
          } 
        })
      }
    },

    logout() {
      store.commit('removeToken')
      this.username = ''
      this.new_username = ''
      this.new_pw = ''
      this.use_case = ''
    },

    // retrieves username info from token
    getTokenUname() {
      token_obj = store.getters.token_obj
      this.username = token_obj.username
    },

    isAdmin() {
      url = DOMAIN + '/genRisks/isAdmin/'

      this.$http.get(url, 
        {headers: {'Authorization': 'JWT ' + store.state.jwt}}).then(response => {

          this.status_msg = response.body
          console.log('isAdmin() = ' + response.body)
          if (TRUE_STR == response.body) {
            this.is_admin_text = 'yes'
            this.is_admin = true
          } else {
            this.is_admin_text = 'no'
            this.is_admin = false
          }

          // update GUI elements from getAllUserNames() for admin
          // privileged users 
          this.handleUseCase()

        }, error => {
          this.status_msg = ERROR + ': isAdmin()'
          this.is_admin = false
      })
    },

    addField: function() {
      var elem = document.createElement('tr')
      this.rows.push(
        {'name': "",
         'type': 'text', // default
         'value': "",
         'saveButDis': false,
         'notNew': false}
      )
      
    },
    
    isValidJson: function(str) {
      try {
          JSON.parse(str)
      } catch (e) {
          return false
      }
      return true
    },

    delField: function(index) {
      if (true == this.isEditRisk) {

        if (true == this.rows[index].notNew) {
          // existing field
          url = DOMAIN + '/genRisks/' + this.user_to_show + '/' +
            this.risk_type + '/' + this.rows[index].type + '/' +
            this.rows[index].name + '/delField/'

          this.$http.get(url,
            {headers: {'Authorization': 'JWT ' + store.state.jwt}}).then(response => {

            this.status_msg = response.body

            if (false == this.status_msg.includes(ERROR)) {
              // update front end (FE)
              this.rows.splice(index, 1)
            }

          }, error => {
            this.status_msg = 'Error delField()'
          })
        } else {
          this.rows.splice(index, 1)

          // ignore delete for new fields not yet added to database
          this.status_msg = 'Field is new (not in database yet). Nothing changed.'
        }
      } else {
        // else if create risk mode, no need to query django back end (BE)
        // just update the FE
        this.rows.splice(index, 1)
      }
      
    },

    /* returns the body of the response from the server
     * on success client / server communication, '' otherwise.
     *
     * Note that the server may in turn return it's own internal error message
     */
    postToEndpoint: function(json_obj, url, error_msg) {
      this.$http.post(url, 
        json_obj, 
        {headers: {'Authorization': 'JWT ' + store.state.jwt}}).then(response => {

          this.status_msg = response.body

        }, error => {
          this.status_msg = error_msg
      })

    },

    /* Same as postToEndpoint() but without
     * {headers: {'Authorization': 'JWT ' + store.state.jwt}}
     */
    postToEndpointNoAuth: function(json_obj, url, error_msg) {
      this.$http.post(url, 
        json_obj).then(response => {

          this.status_msg = response.body

        }, error => {
          this.status_msg = error_msg
      })

    },

    /* If field is new, BE will add it.
     * If field is existing, BE will update it with our modifications
     */
    saveField(index) {
      json_obj = {'user_name': this.user_to_show, 'risk_type': this.risk_type}
      json_obj[FIELDS] = []

      json_obj[FIELDS].push(
         {'name': this.rows[index].name,
          'type': this.rows[index].type,
          'val': this.rows[index].val}
      )

      url = DOMAIN + '/genRisks/saveField/'
      error_msg = ERROR + ': saveField()'

      json_text = JSON.stringify(json_obj);

      this.sending = json_text

      if (this.isValidJson(json_text)) {

        this.$http.post(url, 
          json_obj, 
          {headers: {'Authorization': 'JWT ' + store.state.jwt}}).then(response => {

            this.status_msg = response.body
            // update (FE)
            this.rows[index].saveButDis = true
            this.rows[index].notNew = true 

          }, error => {
            this.status_msg = error_msg
        })

      } else {
        this.status_msg = "Invalid JSON: " + json_text
      }
             
    },

    getInputType: function(in_field_selected) {
      if ('currency' == in_field_selected) {
        return 'number'
      } else {
        return in_field_selected
      }
    },

    enableSaveButton: function(index) {
      this.rows[index].saveButDis = false 

    },

    is_disabled: function(index) {
      return true
    },

    createNewUser: function() {
      this.status_msg = ''

      if (0 == this.new_username.length) {
        this.status_msg = 'User name can not be empty!'

      } else if (0 == this.new_pw.length) {
        this.status_msg = 'password can not be empty!'

      } else {

        if (true == this.new_user_is_admin) {
          new_user_is_admin_text = TRUE_STR
        } else {
          new_user_is_admin_text = FALSE_STR
        }

        json_obj = {'user_name': this.new_username,
          'new_pw': this.new_pw,
          'new_user_is_admin': new_user_is_admin_text}

        url = DOMAIN + '/genRisks/createNewUser/'
        error_msg = ERROR + ': createNewUser()'

        if (0 == this.num_users) {
          // creating first user, bypass authentication
          console.log('0 existing users')
          // no need to set new_user_is_admin_text as it is ignored 
          // and reset to TRUE_STR by server

          this.$http.post(url, json_obj).then(response => {
              this.status_msg = response.body

              this.num_users = 1

            }, error => {
              this.status_msg = error_msg
              // this.num_users still 0
          })


        } else {
          // We're not creating the first user, use authentication

          this.$http.post(url, 
            json_obj, 
            {headers: {'Authorization': 'JWT ' + store.state.jwt}}).then(response => {

              this.status_msg = response.body
              this.num_users += 1

            }, error => {
              this.status_msg = error_msg
          })

        }
      }
    },

    findKeyByVal: function(keyed_arr, val) {

      keys = Object.keys(keyed_arr);
      len = keys.length
      
      for (i = 0; i < len; i++) {
        if (val == keyed_arr[i]) {
          return i
        }
      }
    },

    delUser: function() {
      if (0 == this.user_to_show.length) {
        this.status_msg = 'user name can not be empty!'
      } else {

        json_obj = {"user_name": this.user_to_show}

        url = DOMAIN + '/genRisks/delUser/'

        error_msg = ERROR + ': delUser()'

        this.$http.post(url, 
          json_obj, 
          {headers: {'Authorization': 'JWT ' + store.state.jwt}}).then(response => {

            this.status_msg = response.body
            ind = this.findKeyByVal(this.existing_users, this.user_to_show)
            delete this.existing_users[ind]

            if (this.username == this.user_to_show) {
              // deleting ourself, so remove our token also
              store.commit('removeToken')
            }

            this.username = ''

            this.num_users -= 1

          }, error => {
            this.status_msg = error_msg
        })
      }

    },

    popExistingUsersSelect() {
      if (true == this.is_admin) {
        // admins can see all users
        this.getAllUserNames()
      } else {
        // populate with current (non admin) user only
        this.existing_users = [this.username]
      }

      this.user_to_show = this.username

      // for all users, populate with their risks initially
      if ((this.isEditRisk) ||
         (this.isShowAllRisks)) {
        this.getAllRisksForUser()
      }
    },

    // caution: vue resource runs asynchronously
    getAllUserNames() {
      url = DOMAIN + '/genRisks/getAllUserNames/'
      this.$http.get(url,
        {headers: {'Authorization': 'JWT ' + store.state.jwt}}).then(response => {

        this.existing_users = response.body

        if (0 == this.existing_users.length) {
          this.status_msg = ERROR + ': no existing users' 
          this.user_to_show = ''
        } else {
          this.status_msg = this.existing_users
        }

      }, error => {
        this.status_msg = 'Error getAllUserNames()'
      })
    },

    getSingleRiskWithFields: function() {
      url = DOMAIN + '/genRisks/' + this.user_to_show + '/' +
        this.risk_type + '/getSingleRiskWithFields/'

      this.$http.get(url,
        {headers: {'Authorization': 'JWT ' + store.state.jwt}}).then(response => {
          
        json_obj = response.body
        if (UNDEFINED == json_obj['risk_type']) {
          this.rows = []
        } else {
          len = json_obj[FIELDS].length

          this.rows = []
          for (i = 0; i < len; i++) {
            this.rows.push(
              {'name': json_obj[FIELDS][i].name,
               'type': json_obj[FIELDS][i].type,
               'val': json_obj[FIELDS][i].val,
               'saveButDis': true,
               'notNew': true
              })
          }
        }

      }, error => {
        this.status_msg = 'Error getSingleRiskWithFields()'
      })

    },

    getAllRisksForUser: function() {
      if (this.isEditRisk) {
        url = DOMAIN + '/genRisks/' + this.user_to_show + '/getAllRisks/'

        this.$http.get(url,
          {headers: {'Authorization': 'JWT ' + store.state.jwt}}).then(response => {
          
          this.existing_risks = response.body

          if (0 == this.existing_risks.length) {
            this.status_msg = ERROR + ': No risks found for ' + this.user_to_show
            this.risk_type = ''

            this.rows = []
          } else {
            this.status_msg = this.existing_risks
            this.risk_type = this.existing_risks['0'];

            this.getSingleRiskWithFields()
          }

        }, error => {
          this.status_msg = 'Error getAllRisksForUser()'
        })

      } else if (this.isShowAllRisks) {
        this.getAllRisksWithFields() 
      } else {
        // create risk
        this.rows = []
      }
    },
    
    createRisk: function() {
      this.status_msg = ''

      if (0 == this.rows.length) {
        this.status_msg = 'Please add at least one field!'

      } else {
        json_obj = {'user_name': this.user_to_show, 'risk_type': this.risk_type}
        json_obj[FIELDS] = []

        for (i = 0; i < this.rows.length; i++) {

          json_obj[FIELDS].push(
             {'name': this.rows[i].name,
              'type': this.rows[i].type,
              'val': this.rows[i].val}
          )

        }

        url = DOMAIN + '/genRisks/createRisk/'
        error_msg = ERROR + ': createRisk()'

        this.postToEndpoint(json_obj, url, error_msg)
        

      }
    },

    delRisk: function() {
      url = DOMAIN + '/genRisks/' + this.user_to_show + '/' +
        this.risk_type + '/delRisk/'

      this.$http.get(url,
        {headers: {'Authorization': 'JWT ' + store.state.jwt}}).then(response => {


        // wait until when we get a response from server then try
        this.getAllRisksForUser()
      }, error => {
        this.status_msg = 'Error delRisk()'
      })

    },

    getAllRisksWithFields: function() {
      url = DOMAIN + '/genRisks/' + this.user_to_show + '/getAllRisksWithFields/'
      this.$http.get(url,
        {headers: {'Authorization': 'JWT ' + store.state.jwt}}).then(response => {

        json_obj = response.body

        this.status_msg = json_obj

        // number of risk types
        len = json_obj[ALL_RISKS].length

        this.all_risks_with_fields = []
        // i is risk number
        for (i = 0; i < len; i++) {

          // number of risks fields for each risk type
          len_j = json_obj[ALL_RISKS][i][FIELDS].length

          // temporary storage for "fields" array
          fields_json = []

          for (j = 0; j < len_j; j++) {

            fields_json.push(
              {'name': json_obj[ALL_RISKS][i][FIELDS][j][NAME],
               'type': json_obj[ALL_RISKS][i][FIELDS][j][TYPE],
               'val': json_obj[ALL_RISKS][i][FIELDS][j][VAL]
              }
            )
          }

          this.all_risks_with_fields.push(
            {'risk_type': json_obj[ALL_RISKS][i][RISK_TYPE],
             'fields': fields_json
            }
          )
        }

      }, error => {
        this.status_msg = 'Error getAllRisksWithFields()'
      })
    },

    handleUseCase: function() {
      if (('create_risk' == this.use_case) ||
          ('del_user' == this.use_case) ||
          ('edit_risk' == this.use_case) ||
          ('show_all_risks' == this.use_case)) {

        this.rows = []
        this.risk_type = []

        this.popExistingUsersSelect()
      } 
    },

    getNumUsers() {
      url_num_users = DOMAIN + '/genRisks/getNumUsers/'
      this.$http.get(url_num_users).then(response => {

        this.num_users = parseInt(response.body)

      })
    },

  }, // methods

  mounted() {

    store.dispatch('inspectToken').then(response => {
    })

    this.getNumUsers()
  }

})
