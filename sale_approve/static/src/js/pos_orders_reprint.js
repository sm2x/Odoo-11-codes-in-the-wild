// pos_orders_reprint js
console.log("custom callleddddddddddddddddddddd")
odoo.define('pos_orders_reprint.pos', function(require) {
    "use strict";

    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');
    var core = require('web.core');
    var gui = require('point_of_sale.gui');
    var popups = require('point_of_sale.popups');
    var Model = require('web.DataModel');
    var ActionManagerBrowseinfo = require('web.ActionManager');
    var PaymentScreenWidget = screens.PaymentScreenWidget;
    var QWeb = core.qweb;

    var _t = core._t;


// Load Models here...

    models.load_models({
        model: 'pos.order',
        fields: ['name', 'id', 'date_order', 'partner_id', 'pos_reference', 'lines', 'amount_total', 'session_id', 'state', 'company_id'],
        domain: null,
        loaded: function(self, orders){
        	//console.log("111111111111loadedddddddddddddddddddddddddddddddddddd",orders);
        	self.db.all_orders_list = orders;
        	//console.log("111111111111loadedddddddddddddddddddddddddddddddddddd",orders);

        	self.db.get_orders_by_id = {};
            orders.forEach(function(order) {
                self.db.get_orders_by_id[order.id] = order;
            });

            self.orders = orders;
            //console.log("***************orderssssssssssssssssssssssss", orders);
        },
    });

    models.load_models({
        model: 'pos.order.line',
        fields: ['order_id', 'product_id', 'discount', 'qty', 'price_unit',],
        domain: null,
        loaded: function(self, pos_order_line) {
            //console.log("111111111111loadedddddddddddddddddddddddddddddddddddd",models);
            self.pos_order_line = pos_order_line;
            //console.log("***************self.pos_pos_order_linee", self.pos_order_line);

            //self.db.all_orders_list(orders);
            //console.log("***************orderssssssssssssssssssssssss", orders);
        },
    });



 var ReceiptScreenWidgetNew = screens.ScreenWidget.extend({
       template: 'ReceiptScreenWidgetNew',
        show: function() {
            var self = this;
            self._super();
            $('.button.back').on("click", function() {
                self.gui.show_screen('see_all_orders_screen_widget');
            });
            $('.button.print').click(function() {
                var test = self.chrome.screens.receipt;
                setTimeout(function() { self.chrome.screens.receipt.lock_screen(false); }, 1000);
                if (!test['_locked']) {
                    self.chrome.screens.receipt.print_web();
                    self.chrome.screens.receipt.lock_screen(true);
                }
            });
        }
    });
    gui.define_screen({ name: 'ReceiptScreenWidgetNew', widget: ReceiptScreenWidgetNew });


    // SeeAllOrdersScreenWidget start

    var SeeAllOrdersScreenWidget = screens.ScreenWidget.extend({
        template: 'SeeAllOrdersScreenWidget',
        init: function(parent, options) {
            this._super(parent, options);
            //this.options = {};
        },
        //

        line_selects: function(event,$line,id){
        	//console.log('calllllllll',id);
        	var self = this;
            var orders = this.pos.db.get_orders_by_id[id];
            //console.log("line select orderssssssssssssssssssssssssssssssssssssss", orders);
            this.$('.client-list .lowlight').removeClass('lowlight');
            if ( $line.hasClass('highlight') ){
                $line.removeClass('highlight');
                $line.addClass('lowlight');
                this.display_orders_detail('hide',orders);
                this.new_clients = null;
                //this.toggle_save_button();
            }else{
                this.$('.client-list .highlight').removeClass('highlight');
                $line.addClass('highlight');
                var y = event.pageY - $line.parent().offset().top;
                this.display_orders_detail('show',orders,y);
                this.new_clients = orders;
                //this.toggle_save_button();
            }

        },

        display_orders_detail: function(visibility,order,clickpos){
            var self = this;
            var contents = this.$('.client-details-contents');
            var parent   = this.$('.orders-line ').parent();
            var scroll   = parent.scrollTop();
            var height   = contents.height();

            contents.off('click','.button.edit');
            contents.off('click','.button.save');
            contents.off('click','.button.undo');

            this.editing_client = false;
            this.uploaded_picture = null;

            if(visibility === 'show'){
                contents.empty();
                //console.log('ssssssssssssssssssss',visibility);
                contents.append($(QWeb.render('OrderDetails',{widget:this,order:order})));

                var new_height   = contents.height();

                if(!this.details_visible){
                    if(clickpos < scroll + new_height + 20 ){
                        parent.scrollTop( clickpos - 20 );
                    }else{
                        parent.scrollTop(parent.scrollTop() + new_height);
                    }
                }else{
                    parent.scrollTop(parent.scrollTop() - height + new_height);
                }

                this.details_visible = true;
                //this.toggle_save_button();
            } else if (visibility === 'hide') {
                //console.log('sssssssshhhhhhhssssssssssss hideeeeeeeeeeeeeeeeeeeeeeeeeeeeee',visibility);
                contents.empty();
                if( height > scroll ){
                    contents.css({height:height+'px'});
                    contents.animate({height:0},400,function(){
                        contents.css({height:''});
                    });
                }else{
                    parent.scrollTop( parent.scrollTop() - height);
                }
                this.details_visible = false;
                //this.toggle_save_button();
            }
        },

        get_selected_partner: function() {
            var self = this;
            if (self.gui)
                return self.gui.get_current_screen_param('selected_partner_id');
            else
                return undefined;
        },

         render_list_orders: function(orders){
            //console.log("got ordersssssssssssssssssssssssssssssssssssssss", orders);

            var self = this;
            var selected_partner_id = this.get_selected_partner();
            //console.log("<<<<<<<<<<<<<<<<<<<<<<<selected_partner_id>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",selected_partner_id)
            var selected_client_orders = [];
            if (selected_partner_id != undefined) {
                for (var i = 0; i < orders.length; i++) {
                    if (orders[i].partner_id[0] == selected_partner_id)
                        selected_client_orders = selected_client_orders.concat(orders[i]);
                }
                orders = selected_client_orders;
            }

            var content = this.$el[0].querySelector('.orders-list-contents');
	        //console.log("contentssssssssssssssssssssss", content);
            content.innerHTML = "";
            for(var i = 0, len = Math.min(orders.length,1000); i < len; i++){
                var order    = orders[i];
                var ordersline_html = QWeb.render('OrdersLine',{widget: this, order:orders[i], selected_partner_id: orders[i].partner_id[0]});
                var ordersline = document.createElement('tbody');
                ordersline.innerHTML = ordersline_html;
                ordersline = ordersline.childNodes[1];
                content.appendChild(ordersline);

            }
        },
        //
        show: function(options) {
            var self = this;
            this._super(options);

            this.details_visible = false;

            var orders = self.pos.db.all_orders_list;
            console.log("***************************************ordersssssssssssssss",orders)
            this.render_list_orders(orders, undefined);

	    	this.$('.back').click(function(){
            //self.gui.back();
            self.gui.show_screen('products');

            self.$('.orders-list-contents').delegate('.print-order', 'click', function(result) {
                console.log("clikckkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkked")
                var order_id = parseInt(this.id);
                var orderlines = [];
		        var paymentlines = [];
		        var discount = 0;
                //console.log("order_iddddddddddddddddddddddddddddddddddddddddd",order_id)

                var selectedOrder = null;
		        for(var i = 0, len = Math.min(orders.length,1000); i < len; i++) {
		            if (orders[i] && orders[i].id == order_id) {
		                selectedOrder = orders[i];
		                console.log("selectedOrder_newewwwwwwwwwwwwwwwwwwwwwwwwwwwww",selectedOrder)
		            }
		        }

            //if (self.pos.config.pos_order_reprint == 'ticket') {
              (new Model('pos.order')).call('print_pos_receipt', [order_id]).fail(function(unused, event) {
                    //alert('Connection Error. Try again later !!!!');
                }).done(function(output) {

                    console.log("outputttttttttttttttttttttt", output)
		            //var selectedOrder = self.pos.get('selectedOrder');
					//console.log("order_iddddddddddddddddddddddddddddddddddddddddd",selectedOrder)

					orderlines = output[0];
		            paymentlines = output[2];
		            discount = output[1];
		            self.gui.show_screen('ReceiptScreenWidgetNew');
		            $('.pos-receipt-container').html(QWeb.render('PosTicket1',{
		                widget:self,
		                order: selectedOrder,
		                paymentlines: paymentlines,
		                orderlines: orderlines,
		                discount_total: discount,
		                change: output[3],
		            }));


				});
			//}

			/*if (self.pos.config.pos_order_reprint == 'pdf') {

                (new Model('pos.order')).call('print_pos_report', [order_id]).fail(function(unused, event) {
                    //alert('Connection Error. Try again later !!!!');
                }).done(function(output) {

                    console.log("outputttttttttttttttttttttt", output)
                    this.action_manager = new ActionManagerBrowseinfo(this);
                    //console.log("this.action_managerdddddddddddddddd",this.action_manager)
                        this.action_manager.do_action(output, {
                            additional_context: {
                                active_id: order_id,
                                active_ids: [order_id],
                                active_model: 'pos.order'
                            }
                        })

				});
			}*/


            });

            var contents = self.$('.orders-list-contents');
            contents.empty();
            var parent = self.$('.client-list').parent();
            //console.log("***************************************parenttttttttttttt",parent)
            parent.scrollTop(0);

        });

        },
        //


    });
    gui.define_screen({
        name: 'see_all_orders_screen_widget',
        widget: SeeAllOrdersScreenWidget
    });

    // End SeeAllOrdersScreenWidget



	// Start SeeAllOrdersButtonWidget

    var SeeAllOrdersButtonWidget = screens.ActionButtonWidget.extend({
        template: 'SeeAllOrdersButtonWidget',

        button_click: function() {
            var self = this;
            this.gui.show_screen('see_all_orders_screen_widget', {});
        },

    });

    screens.define_action_button({
        'name': 'See All Orders Button Widget',
        'widget': SeeAllOrdersButtonWidget,
        'condition': function() {
            return true;
        },
    });
    // End SeeAllOrdersButtonWidget

// Start ClientListScreenWidget
		gui.Gui.prototype.screen_classes.filter(function(el) { return el.name == 'clientlist'})[0].widget.include({
            show: function(){
		        this._super();
		        var self = this;
		        this.$('.view-orders').click(function(){
		        	//console.log("callledddddddddddddddddddddddddddddddddddddddddd all orderssssssssssss")
            		self.gui.show_screen('see_all_orders_screen_widget', {});
            	});


            $('.selected-client-orders').on("click", function() {
                self.gui.show_screen('see_all_orders_screen_widget', {
                    'selected_partner_id': this.id
                });
            });

        },
    });


});
