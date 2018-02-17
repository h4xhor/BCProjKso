const DOMAIN = 'https://t4yj00k07h.execute-api.ap-southeast-2.amazonaws.com/dev'

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

var app = new Vue({
  el: "#app",

  // state
  data: {
    use_case: 'del_cust',
    new_cust_name: 'Don Joe',

    existing_customers: [],
    cur_cust: '',

    risk_type: 'Automobile',

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
    status_msg: '',
  },

  // computed properties
  computed: {
    isCreateCust: function() {
      return "create_cust" == this.use_case
    },

    isDelCust: function() {
      return "del_cust" == this.use_case
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
      if (this.isCreateCust) {
        msg = "Creates a new customer and saves to database."
      } else if (this.isDelCust) {
        msg = "Deletes an existing customer."
      } else if (this.isCreateRisk) {
        msg = "Creates a new risk type for an existing customer."
      } else if (this.isEditRisk) {
        msg = "Edit or delete an existing risk type (for an existing customer)."
      } else if (this.isShowAllRisks) {
        msg = 'Shows all risk types and their fields'
      } else {
        msg = ERROR + ': Non existent mode'
      }

      return msg
    }

  },

  methods: {
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
          url = DOMAIN + '/genRisks/' + this.cur_cust + '/' +
            this.risk_type + '/' + this.rows[index].type + '/' +
            this.rows[index].name + '/delField/'

          this.$http.get(url).then(response => {

            this.status_msg = response.body

            if (false == this.status_msg.includes(ERROR)) {
              // update front end (FE)
              this.rows.splice(index, 1)
            }

          }, response => {
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

      json_text = JSON.stringify(json_obj);

      this.sending = json_text

      if (this.isValidJson(json_text)) {

        this.$http.post(url, 
          json_text, 
          {emulateJSON: true}).then(response => {

            this.status_msg = response.body
          }, response => {
            this.status_msg = error_msg
        })

      } else {
        this.status_msg = "Invalid JSON: " + json_text
      }

    },

    /* If field is new, BE will add it.
     * If field is existing, BE will update it with our modifications
     */
    saveField: function(index) {
      json_obj = {'customer_name': this.cur_cust, 'risk_type': this.risk_type}
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
          json_text, 
          {emulateJSON: true}).then(response => {

            this.status_msg = response.body
            // update (FE)
            this.rows[index].saveButDis = true
            this.rows[index].notNew = true 

          }, response => {
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

    createNewCust: function() {
      this.status_msg = ''

      if (0 == this.new_cust_name.length) {
        this.status_msg = 'Customer name can not be empty!'

      } else {
        json_obj = {"customer_name": this.new_cust_name}


        url = DOMAIN + '/genRisks/createNewCust/'
        error_msg = ERROR + ': createNewCust()'

        this.postToEndpoint(json_obj, url, error_msg)
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

    delCust: function() {
      if (0 == this.new_cust_name.length) {
        this.status_msg = 'Customer name can not be empty!'
      } else {

        json_obj = {"customer_name": this.cur_cust}

        url = DOMAIN + '/genRisks/delCust/'

        error_msg = ERROR + ': delCust()'

        json_text = JSON.stringify(json_obj);

        this.sending = json_text

        if (this.isValidJson(json_text)) {

          this.$http.post(url, 
            json_text, 
            {emulateJSON: true}).then(response => {

              this.status_msg = response.body
              ind = this.findKeyByVal(this.existing_customers, this.cur_cust)
              delete this.existing_customers[ind]

            }, response => {
              this.status_msg = error_msg
          })

        } else {
          this.status_msg = "Invalid JSON: " + json_text
        }
      }

    },

    // caution: vue resource runs asynchronously
    getAllExistingCust: function() {
      url = DOMAIN + '/genRisks/getAllCustNames/'
      this.$http.get(url).then(response => {
      //Vue.http.get(url).then(response => {

        this.existing_customers = response.body

        if (0 == this.existing_customers.length) {
          this.status_msg = ERROR + ': no existing customers' 
          this.cur_cust = ''
        } else {
          this.status_msg = this.existing_customers
          this.cur_cust = this.existing_customers['0'];
          if ((this.isEditRisk) ||
             (this.isShowAllRisks)) {
            // wait until when we get a response from server then try
            this.getAllRisksForCust()
          }
        }

      }, response => {
        this.status_msg = 'Error getAllExistingCust()'
      })
    },

    getSingleRiskWithFields: function() {
      url = DOMAIN + '/genRisks/' + this.cur_cust + '/' +
        this.risk_type + '/getSingleRiskWithFields/'
      this.$http.get(url).then(response => {
          
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

      }, response => {
        this.status_msg = 'Error getSingleRiskWithFields()'
      })

    },

    getAllRisksForCust: function() {
      if (this.isEditRisk) {
        url = DOMAIN + '/genRisks/' + this.cur_cust + '/getAllRisks/'

        this.$http.get(url).then(response => {
          
          this.existing_risks = response.body

          if (0 == this.existing_risks.length) {
            this.status_msg = ERROR + ': No risks found for ' + this.cur_cust
            this.risk_type = ''

            this.rows = []
          } else {
            this.status_msg = this.existing_risks
            this.risk_type = this.existing_risks['0'];

            this.getSingleRiskWithFields()
          }

        }, response => {
          this.status_msg = 'Error getAllRisksForCust()'
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
        json_obj = {'customer_name': this.cur_cust, 'risk_type': this.risk_type}
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
      url = DOMAIN + '/genRisks/' + this.cur_cust + '/' +
        this.risk_type + '/delRisk/'

      this.$http.get(url).then(response => {


        // wait until when we get a response from server then try
        this.getAllRisksForCust()
      }, response => {
        this.status_msg = 'Error delRisk()'
      })

    },

    getAllRisksWithFields: function() {
      url = DOMAIN + '/genRisks/' + this.cur_cust + '/getAllRisksWithFields/'
      this.$http.get(url).then(response => {

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

      }, response => {
        this.status_msg = 'Error getAllRisksWithFields()'
      })
    },

    handleUseCase: function() {
      if (('create_risk' == this.use_case) ||
          ('del_cust' == this.use_case) ||
          ('edit_risk' == this.use_case) ||
          ('show_all_risks' == this.use_case)) {

        this.rows = []
        this.risk_type = []

        this.getAllExistingCust()


      } 
    },
  },

  mounted: function() {
    this.handleUseCase()
  }

})
